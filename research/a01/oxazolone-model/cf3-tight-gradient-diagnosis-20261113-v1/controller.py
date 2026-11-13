"""Five fixed-M0 tight-SCF/gradient probes within one immutable resource window."""
from datetime import datetime, timezone
import hashlib
import json
import math
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
RAW = ROOT/'scratch/m0-cf3-tight-gradient-diagnosis-20261113-v1'
CONTRACT = HERE/'contract.v1.json'
WORKER = HERE/'worker_points.py'
MANIFEST = HERE/'launch-manifest.v1.json'
HISTORY = 20.55026662453337
STAGE = 'TIGHT_GRADIENT'


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def local(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT/path


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


def emit(value):
    print(json.dumps(value, ensure_ascii=False, allow_nan=False), flush=True)


def reserve_counter(budget, point_id, output, now):
    if now >= budget['deadline_epoch'] or budget['total_scf_attempts'] >= 5 or budget['gradient_reservations'] >= 5:
        raise RuntimeError('Fixed global wall or five-call cap reached')
    identifier = budget['total_scf_attempts']+1
    budget['total_scf_attempts'] += 1; budget['gradient_reservations'] += 1
    budget['reservations'].append({'id':identifier,'stage':STAGE,'point_id':point_id,
        'worker_output':str(output),'reserved_epoch':now})
    budget['events'].append({'event':'reserve','reservation_id':identifier,
        'stage':STAGE,'point_id':point_id,'epoch':now})
    return identifier


def displacement_admission(budget, center_gate, now):
    reasons = []
    if center_gate.get('passed') is not True:
        reasons.append('center_identity_electronic_completeness_or_raw_gradient_gate_failed')
    if 5-budget['total_scf_attempts'] < 4 or 5-budget['gradient_reservations'] < 4:
        reasons.append('fewer_than_four_complete_point_slots')
    if budget['deadline_epoch']-now < 1980:
        reasons.append('less_than_1980_seconds_for_four_points_and_cleanup')
    return {'admitted':not reasons,'reasons':reasons,
        'remaining_seconds':budget['deadline_epoch']-now,
        'original_or_current_bad_curvature_is_not_a_gate':True}


def center_gradient_gate(gradient):
    import numpy as np
    g = np.asarray(gradient)
    if g.shape != (26,3) or not np.all(np.isfinite(g)):
        return {'passed':False,'reason':'incomplete_or_nonfinite_center_gradient'}
    atom = np.linalg.norm(g,axis=1)
    rms, maximum = float(np.sqrt(np.mean(atom*atom))),float(atom.max())
    return {'passed':rms <= 3e-4 and maximum <= 4.5e-4,
        'atom_norm_RMS_Eh_bohr':rms,'atom_norm_max_Eh_bohr':maximum,
        'RMS_threshold_Eh_bohr':3e-4,'max_threshold_Eh_bohr':4.5e-4,
        'role':'Raw center force-balance diagnostic only, not curvature or orbital stability'}


def terminate_and_wait(process):
    if process.poll() is None:
        try: os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError: pass
        try: return process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try: os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError: pass
    return process.wait()


def main():
    if sys.platform != 'linux':
        raise RuntimeError('Existing Linux/WSL backend and process groups required')
    manifest = read(MANIFEST)
    for item in manifest['files']:
        source = HERE/item['path']
        if sha(source) != item['sha256'] or source.stat().st_size != item['size_bytes']:
            raise RuntimeError('Reviewed launch source differs: '+item['path'])
    pins = {'controller':sha(Path(__file__)),'worker':sha(WORKER),'contract':sha(CONTRACT),'manifest':sha(MANIFEST)}
    contract = read(CONTRACT)
    plan_path = local(contract['source_plan']); plan = read(plan_path)
    plan_sha = contract['source_plan_sha256']
    if sha(plan_path) != plan_sha or pins['worker'] != contract['worker_sha256']:
        raise RuntimeError('Archived fixed input or worker changed')
    expected_limits = {'shared_wall_seconds':3000,'per_point_wall_seconds':480,
        'max_SCF_attempts':5,'max_gradient_reservations':5,'max_workers':1,
        'threads_per_worker':4,'memory_mb_soft_per_worker':4000,'max_SCF_cycles_per_point':120}
    if contract['limits'] != expected_limits or contract['historical_recorded_worker_hours_lower_bound'] != HISTORY:
        raise RuntimeError('Reviewed cumulative resource limits differ')
    inputs_path = HERE/contract['inputs']
    if sha(inputs_path)!=contract['inputs_sha256'] or read(inputs_path)['points']!=plan['points']:
        raise RuntimeError('Reviewed five-point input identity differs')
    expected_points = ['center','C6-y-plus','C6-y-minus','C10-y-plus','C10-y-minus']
    if [point['point_id'] for point in plan['points']] != expected_points:
        raise RuntimeError('This controller admits only the five reviewed fixed points')

    def check_source_pins():
        if pins != {'controller':sha(Path(__file__)),'worker':sha(WORKER),'contract':sha(CONTRACT),'manifest':sha(MANIFEST)} or sha(plan_path)!=plan_sha or sha(inputs_path)!=contract['inputs_sha256']:
            raise RuntimeError('Immutable execution source or plan changed')
        for item in plan['accessed_source_fingerprints']:
            source = local(item['path'])
            if sha(source) != item['sha256'] or source.stat().st_size != item['size_bytes']:
                raise RuntimeError('Saved scientific input changed: '+item['path'])

    check_source_pins()
    if RAW.exists():
        raise FileExistsError('Existing batch cannot be overwritten or renamed to reset its calls')
    RAW.mkdir()
    for name in ['specs','points','processes']:
        (RAW/name).mkdir()
    for source in [CONTRACT,WORKER,Path(__file__).resolve(),MANIFEST]:
        shutil.copyfile(source,RAW/('snapshot-'+source.name))
    os.environ.update(OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1')
    import numpy as np
    start = time.time(); deadline = start+3000
    budget = {'contract_sha256':pins['contract'],'plan_sha256':plan_sha,
        'started_epoch':start,'deadline_epoch':deadline,'total_scf_attempts':0,
        'SCF_started':0,'SCF_complete':0,'gradient_reservations':0,'gradient_started':0,
        'completed_gradients':0,'reservations':[],'events':[]}
    budget_path = RAW/'shared-budget.json';save(budget_path,budget,exclusive=True)
    result = {'schema_version':'1.0','task_id':contract['task_id'],
        'scientific_review_status':'review_required','release_eligible':False,'status':'running',
        'started_epoch':start,'execution_commit':None,'execution_code_sha256':pins,
        'processes':[],'center_gradient_gate':None,'displacement_admission':None,
        'stop_reason':None,'full_Hessian_qualified':False,'formal_IRC':'not_performed',
        'target_saddle_or_mechanism':'not_performed','model_API_called':False}
    seen = set(); stopped = False; active = None

    def stop(signum, frame):
        nonlocal stopped
        stopped = True; result['stop_reason']='external_controller_signal_'+str(signum)
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)

    def account(row, reservation):
        for flag,event,counter in [('scf_started','SCF_started','SCF_started'),
                ('electronic_complete','SCF_complete','SCF_complete'),
                ('gradient_started','gradient_started','gradient_started'),
                ('gradient_complete','gradient_completed','completed_gradients')]:
            key = (reservation['id'],event)
            if row.get(flag) is True and key not in seen:
                seen.add(key);budget[counter] += 1
                budget['events'].append({'event':event,'reservation_id':reservation['id'],
                    'stage':STAGE,'point_id':reservation['point_id'],'epoch':time.time(),
                    'time_role':'Controller observation, not exact native entry timestamp'})
                save(budget_path,budget)

    def run_point(point):
        nonlocal active
        point_id = point['point_id']; output = RAW/'points'/point_id
        check_source_pins()
        if read(budget_path)!=budget:
            raise RuntimeError('Shared budget changed outside its controller')
        if stopped or time.time()+60>=deadline:
            raise TimeoutError('No complete point admitted before the fixed deadline')
        identifier = reserve_counter(budget,point_id,output,time.time());save(budget_path,budget)
        reservation = budget['reservations'][-1]
        spec = {'stage':STAGE,'point_id':point_id,'plan_path':str(plan_path),
            'plan_sha256':plan_sha,'contract_path':str(CONTRACT),
            'contract_sha256':pins['contract'],'reservation_id':identifier,
            'shared_budget_path':str(budget_path),'global_started_epoch':start,
            'global_deadline_epoch':deadline,'expected_worker_sha256':pins['worker']}
        spec_path = RAW/'specs'/(point_id+'.json');save(spec_path,spec,exclusive=True)
        process = {'stage':STAGE,'point_id':point_id,'reservation_id':identifier,
            'output':str(output),'result_path':str(output/'result.json'),'started_epoch':time.time(),
            'returncode':None,'timed_out':False,'external_stop':False,
            'stdout':str(RAW/'processes'/(point_id+'.stdout.log')),
            'stderr':str(RAW/'processes'/(point_id+'.stderr.log'))}
        child=None;row={}
        with Path(process['stdout']).open('xb') as stdout,Path(process['stderr']).open('xb') as stderr:
            try:
                child=subprocess.Popen([sys.executable,'-u',str(WORKER),str(spec_path),str(output)],
                    cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,start_new_session=True)
                active=child;point_deadline=min(process['started_epoch']+480,deadline-30)
                while child.poll() is None:
                    if (output/'result.json').exists():
                        row=read(output/'result.json');account(row,reservation)
                    if stopped or time.time()>=point_deadline:
                        process['timed_out']=not stopped;process['external_stop']=stopped
                        terminate_and_wait(child);break
                    time.sleep(.5)
                process['returncode']=child.wait()
            except BaseException as exc:
                process['controller_error']=repr(exc)
                if child is not None:process['returncode']=terminate_and_wait(child)
                raise
            finally:
                active=None;process['finished_epoch']=time.time()
                process['elapsed_seconds']=process['finished_epoch']-process['started_epoch']
                if (output/'result.json').exists():
                    row=read(output/'result.json');account(row,reservation)
                    process['worker_result_sha256']=sha(output/'result.json')
                    process['worker_status']=row.get('status')
                    for key in ['scf_started','electronic_complete','gradient_started','gradient_complete']:
                        process[key]=row.get(key)
                save(RAW/'processes'/(point_id+'.json'),process,exclusive=True)
                result['processes'].append(process);save(RAW/'campaign-status.json',result)
                emit({'point_id':point_id,'returncode':process['returncode'],
                    'status':row.get('status'),'elapsed_seconds':process['elapsed_seconds']})
        if process['returncode']!=0 or process['timed_out'] or process['external_stop']:
            raise RuntimeError('Point failed or stopped: '+point_id)
        if row.get('stage')!=STAGE or row.get('point_id')!=point_id or row.get('reservation_id')!=identifier:
            raise RuntimeError('Returned point identity differs')
        if not all(row.get(k) is True for k in ['scf_converged','identity_checks_passed',
                'strict_final_orbital_diagnostic_passed','gradient_complete']):
            raise RuntimeError('Incomplete or unqualified electronic/gradient point: '+point_id)
        if not np.allclose(np.asarray(row['coordinates_bohr']),np.asarray(point['coordinates_bohr']),rtol=0,atol=1e-12):
            raise RuntimeError('Fixed-point coordinates changed')
        if sha(output/'gradient.npy')!=row.get('gradient_npy_sha256'):
            raise RuntimeError('Returned gradient bytes differ')
        gradient=np.load(output/'gradient.npy',allow_pickle=False)
        if gradient.shape!=(26,3) or not np.all(np.isfinite(gradient)):
            raise RuntimeError('Returned gradient has invalid shape or nonfinite components')
        check_source_pins()
        return row,gradient

    code=2
    try:
        row,gradient=run_point(plan['points'][0])
        gate=center_gradient_gate(gradient)
        gate['worker_flag_agrees']=row.get('center_gradient_check_passed')==gate['passed']
        if not gate['worker_flag_agrees']:gate['passed']=False
        result['center_gradient_gate']=gate;save(RAW/'campaign-status.json',result)
        if not gate['passed']:
            result['stop_reason']='center_raw_gradient_gate_failed';raise RuntimeError(result['stop_reason'])
        result['displacement_admission']=displacement_admission(budget,gate,time.time())
        save(RAW/'campaign-status.json',result);emit({'displacement_admission':result['displacement_admission']})
        if not result['displacement_admission']['admitted']:
            result['stop_reason']='four_displacements_not_admitted';raise RuntimeError(result['stop_reason'])
        for point in plan['points'][1:]:run_point(point)
        result['status']='completed_five_point_diagnosis';result['stop_reason']='five_fixed_points_complete';code=0
    except BaseException as exc:
        result['status']='stopped_or_failed_with_partial_evidence';result['error']=repr(exc)
        result['stop_reason']=result['stop_reason'] or repr(exc)
        (RAW/'controller-failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
    finally:
        if active is not None:terminate_and_wait(active)
        result['finished_epoch']=time.time();result['wall_elapsed_seconds']=result['finished_epoch']-start
        result['workers_elapsed_seconds']=sum(p['elapsed_seconds'] for p in result['processes'])
        result['historical_worker_hours_lower_bound']=HISTORY
        result['known_worker_hours_lower_bound_including_this_batch']=HISTORY+result['workers_elapsed_seconds']/3600
        result['budget_snapshot']=budget;result['controller_intended_returncode']=code
        save(RAW/'controller-result.json',result,exclusive=True);save(RAW/'campaign-status.json',result)
        emit({'status':result['status'],'stop_reason':result['stop_reason'],
            'worker_seconds':result['workers_elapsed_seconds'],'SCF':budget['SCF_started'],
            'gradients':budget['completed_gradients'],'controller_intended_returncode':code})
    return code


if __name__=='__main__':
    sys.exit(main())
