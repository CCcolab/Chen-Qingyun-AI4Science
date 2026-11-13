"""One 600-second shared window, one SCF reservation, zero nuclear gradients."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT/'scratch/m0-cf3-center-terminal-scf-20261113-v1'
CONTRACT = HERE/'contract.v1.json'
WORKER = HERE/'worker_scf.py'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def save(path, value, exclusive=False):
    data = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')
    if exclusive:
        with path.open('xb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
    else:
        temporary = path.with_name(path.name+'.partial-'+str(os.getpid()))
        with temporary.open('wb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)


def reserve_one(budget, output, now):
    if budget['total_scf_attempts'] != 0 or now >= budget['deadline_epoch']:
        raise RuntimeError('One-call cap or fixed deadline reached; no refund/retry')
    if any(budget[k] != 0 for k in ['gradient_reservations','gradient_started','completed_gradients']):
        raise RuntimeError('No nuclear-gradient reservations or calls allowed')
    budget['total_scf_attempts'] = 1
    row = {'id': 1, 'stage': 'CENTER_SCF_ONLY', 'point_id': 'center', 'worker_output': str(output), 'reserved_epoch': now}
    budget['reservations'].append(row)
    budget['events'].append({'event': 'reserve', 'reservation_id': 1, 'epoch': now})


def terminate_and_wait(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            return process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    return process.wait()


def main():
    if sys.platform != 'linux':
        raise RuntimeError('Real Linux/WSL process-group watchdog required')
    contract = read(CONTRACT)
    if sha(WORKER) != contract['worker_sha256']:
        raise RuntimeError('Worker differs from sealed contract')
    plan_path = ROOT/contract['plan_source']
    if sha(plan_path) != contract['plan_sha256']:
        raise RuntimeError('Archived center plan differs')
    plan = read(plan_path)
    for item in plan['accessed_source_fingerprints']:
        path = ROOT/item['path']
        if sha(path) != item['sha256'] or path.stat().st_size != item['size_bytes']:
            raise RuntimeError('Input scientific source changed: '+item['path'])
    if RAW.exists():
        raise FileExistsError('Existing trial cannot be overwritten or rerun under a new name')
    original_code = {'controller': sha(Path(__file__)), 'worker': sha(WORKER), 'contract': sha(CONTRACT)}
    RAW.mkdir()
    for source in [CONTRACT, WORKER, Path(__file__).resolve()]:
        shutil.copyfile(source, RAW/('snapshot-'+source.name))
    start = time.time(); deadline = start+600
    output = RAW/'point'
    budget = {'contract_sha256': sha(CONTRACT), 'plan_sha256': sha(plan_path),
        'started_epoch': start, 'deadline_epoch': deadline, 'total_scf_attempts': 0,
        'SCF_started': 0, 'SCF_complete': 0, 'gradient_reservations': 0,
        'gradient_started': 0, 'completed_gradients': 0, 'reservations': [], 'events': []}
    reserve_one(budget, output, time.time())
    save(RAW/'shared-budget.json', budget, exclusive=True)
    spec = {'stage': 'CENTER_SCF_ONLY', 'point_id': 'center', 'plan_path': str(plan_path),
        'plan_sha256': sha(plan_path), 'contract_path': str(CONTRACT), 'contract_sha256': sha(CONTRACT),
        'reservation_id': 1, 'shared_budget_path': str(RAW/'shared-budget.json'),
        'global_started_epoch': start, 'global_deadline_epoch': deadline, 'expected_worker_sha256': sha(WORKER)}
    save(RAW/'requested-spec.json', spec, exclusive=True)
    process_record = {'started_epoch': time.time(), 'returncode': None, 'timed_out': False,
        'external_stop': False, 'output': str(output), 'SCF_reservations': 1, 'gradient_reservations': 0}
    process = None; row = {}; failure = None; seen = set(); STOP = False

    def stop(signum, frame):
        nonlocal STOP
        STOP = True

    signal.signal(signal.SIGINT, stop); signal.signal(signal.SIGTERM, stop)

    def account(result):
        for flag, event, counter in [('scf_started','SCF_started','SCF_started'), ('electronic_complete','SCF_complete','SCF_complete')]:
            if result.get(flag) is True and event not in seen:
                seen.add(event); budget[counter] += 1
                budget['events'].append({'event': event, 'reservation_id': 1, 'epoch': time.time(), 'time_role': 'controller observation'})
        save(RAW/'shared-budget.json', budget)

    with (RAW/'stdout.log').open('xb') as stdout, (RAW/'stderr.log').open('xb') as stderr:
        try:
            process = subprocess.Popen([sys.executable, '-u', str(WORKER), str(RAW/'requested-spec.json'), str(output)],
                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
            point_deadline = min(process_record['started_epoch']+480, deadline-30)
            while process.poll() is None:
                if (output/'result.json').exists():
                    row = read(output/'result.json'); account(row)
                if STOP or time.time() >= point_deadline:
                    process_record['timed_out'] = not STOP; process_record['external_stop'] = STOP
                    terminate_and_wait(process); break
                time.sleep(.5)
            process_record['returncode'] = process.wait()
        except BaseException as exc:
            failure = repr(exc)
            if process is not None:
                process_record['returncode'] = terminate_and_wait(process)
            (RAW/'controller-failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        finally:
            process_record['finished_epoch'] = time.time()
            process_record['elapsed_seconds'] = process_record['finished_epoch']-process_record['started_epoch']
            if (output/'result.json').exists():
                row = read(output/'result.json'); account(row)
                process_record['worker_result_sha256'] = sha(output/'result.json')
            save(RAW/'process-result.json', process_record, exclusive=True)
    integrity = all(sha(ROOT/item['path']) == item['sha256'] and (ROOT/item['path']).stat().st_size == item['size_bytes'] for item in plan['accessed_source_fingerprints'])
    integrity = integrity and original_code == {'controller': sha(Path(__file__)), 'worker': sha(WORKER), 'contract': sha(CONTRACT)}
    passed = (failure is None and process_record['returncode'] == 0 and not process_record['timed_out']
        and not process_record['external_stop'] and time.time() <= deadline and integrity
        and row.get('center_electronic_check_passed') is True and row.get('final_electron_count') == 154
        and row.get('gradient_started') is False and row.get('nuclear_gradient_calls') == 0
        and budget['total_scf_attempts'] == budget['SCF_started'] == budget['SCF_complete'] == 1)
    result = {'schema_version': '1.0', 'task_id': contract['task_id'], 'scientific_review_status': 'review_required',
        'release_eligible': False, 'status': 'center_electronic_terminal_check_passed' if passed else 'single_center_trial_stopped_unqualified',
        'center_electronic_check_passed': passed, 'started_epoch': start, 'finished_epoch': time.time(),
        'execution_commit': None, 'controller_sha256': sha(Path(__file__)), 'worker_sha256': sha(WORKER),
        'contract_sha256': sha(CONTRACT), 'source_integrity_after': integrity, 'process': process_record,
        'worker_result': row, 'budget_snapshot': budget, 'error': failure,
        'wall_elapsed_seconds': time.time()-start, 'worker_elapsed_seconds': process_record['elapsed_seconds'],
        'historical_worker_hours_lower_bound': contract['historical_recorded_worker_hours_lower_bound'],
        'cumulative_recorded_worker_hours_lower_bound': contract['historical_recorded_worker_hours_lower_bound']+process_record['elapsed_seconds']/3600,
        'full_Hessian_qualified': False, 'SCF_effect_on_reciprocal_error': 'unknown', 'cause': 'unknown',
        'nuclear_gradient_calls': 0, 'following_quantum_stage': 'not_started',
        'controller_intended_returncode': 0 if passed else 2}
    save(RAW/'result.json', result, exclusive=True)
    print(json.dumps({'status': result['status'], 'terminal_orbital_norm': row.get('final_scf_diagnostics',{}).get('orbital_gradient_backend_norm'),
        'worker_returncode': process_record['returncode'], 'worker_elapsed_seconds': process_record['elapsed_seconds'],
        'cumulative_lower_bound': result['cumulative_recorded_worker_hours_lower_bound'], 'gradient_calls': 0}), flush=True)
    return 0 if passed else 2


if __name__ == '__main__':
    sys.exit(main())
