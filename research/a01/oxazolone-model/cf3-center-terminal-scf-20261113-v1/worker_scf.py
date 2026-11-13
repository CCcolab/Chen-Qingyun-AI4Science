"""Exactly one reserved, fixed-M0 CF3 center SCF; no nuclear derivative entry.

Linux/WSL execution only. The controller owns the shared immutable-deadline
ledger and reserves one SCF and zero nuclear gradients before spawning this worker.
Importing this module or --validate-only never imports a quantum backend.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PLAN = HERE.parent / 'cf3-curvature-diagnosis-20261113-v1/planned-inputs.v2.json'
CONTRACT = HERE / 'contract.v1.json'
PLAN_SHA = 'b00db278cc3d219b5c1aac5778ee7b36a469be7fc84d307598c7ffbe7a8524de'
SYMBOLS = 'O C O C C C C C C C N C C C F F F C F F F H H H H H'.split()
MAPS = list(range(1, 15)) + [16, 17, 18, 15, 19, 20, 21] + list(range(100, 105))
POINTS = ['center']
BOHR_A = .52917721092


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def plain(value):
    if hasattr(value, 'tolist'):
        return plain(value.tolist())
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    temporary = path.with_name(path.name + '.partial-' + str(os.getpid()))
    with temporary.open('w', encoding='utf-8', newline='\n') as stream:
        json.dump(plain(value), stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def local(value):
    text = str(value)
    if os.name == 'nt' and text.startswith('/mnt/') and len(text) > 7 and text[6] == '/':
        text = text[5].upper() + ':/' + text[7:]
    elif os.name != 'nt' and len(text) > 2 and text[1] == ':' and text[2] in '/\\':
        text = '/mnt/' + text[0].lower() + '/' + text[3:].replace('\\', '/')
    path = Path(text)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(spec, output, require_live=True):
    if spec.get('stage') != 'CENTER_SCF_ONLY' or spec.get('point_id') != 'center':
        raise ValueError('Only this single fixed CF3 center SCF trial is accepted')
    if local(spec.get('plan_path', '')) != PLAN or spec.get('plan_sha256') != PLAN_SHA or sha(PLAN) != PLAN_SHA:
        raise ValueError('Unexpected immutable input plan')
    if local(spec.get('contract_path', '')) != CONTRACT or spec.get('contract_sha256') != sha(CONTRACT):
        raise ValueError('Unexpected immutable diagnostic contract')
    if spec.get('expected_worker_sha256') != sha(Path(__file__).resolve()):
        raise ValueError('Worker code differs from reviewed execution identity')
    if not output.is_relative_to((ROOT / 'scratch').resolve()):
        raise ValueError('Worker output must remain inside project scratch')
    if output.exists():
        raise FileExistsError('Existing output is immutable; refuse without modification')
    reservation = spec.get('reservation_id')
    if not isinstance(reservation, int) or isinstance(reservation, bool) or reservation != 1:
        raise ValueError('Invalid precharged reservation')
    start, deadline = spec.get('global_started_epoch'), spec.get('global_deadline_epoch')
    if not finite(start) or not finite(deadline) or not 0 < deadline - start <= 600.000001:
        raise ValueError('Missing or extended cumulative deadline')
    if require_live and time.time() >= deadline:
        raise TimeoutError('Shared diagnostic deadline expired')
    budget_path = local(spec.get('shared_budget_path', ''))
    if not budget_path.is_relative_to((ROOT / 'scratch').resolve()):
        raise ValueError('Shared ledger must be project scratch evidence')
    budget = read(budget_path)
    for key, expected in [('started_epoch', start), ('deadline_epoch', deadline),
                          ('contract_sha256', spec['contract_sha256']), ('plan_sha256', PLAN_SHA)]:
        if budget.get(key) != expected:
            raise ValueError('Shared ledger identity differs: ' + key)
    if budget.get('total_scf_attempts') != 1 or budget.get('gradient_reservations') != 0 or budget.get('gradient_started') != 0 or budget.get('completed_gradients') != 0:
        raise ValueError('Shared reservation counts are absent or exceed contract')
    rows = [r for r in budget.get('reservations', []) if r.get('id') == reservation]
    if len(rows) != 1 or rows[0].get('stage') != spec['stage'] or rows[0].get('point_id') != spec['point_id'] or local(rows[0].get('worker_output', '')) != output:
        raise ValueError('Reservation does not belong to this stage/point/output')
    contract = read(CONTRACT)
    required_limits = {'shared_wall_seconds': 600, 'per_point_wall_seconds': 480,
        'max_SCF_attempts': 1, 'max_gradient_reservations': 0, 'max_workers': 1,
        'threads_per_worker': 4, 'memory_mb_soft_per_worker': 4000, 'max_SCF_cycles_per_point': 120}
    if contract.get('limits') != required_limits or contract.get('internal_targets') != {'conv_tol': 1e-12, 'conv_tol_grad': 1e-10} or contract.get('final_orbital_norm_max') != 1e-9:
        raise ValueError('Unexpected fixed SCF-only contract')
    plan = read(PLAN)
    manifest = plan.get('species_manifest')
    if manifest != {'formula': 'C12H5F6NO2', 'symbols': SYMBOLS, 'atom_maps': MAPS}:
        raise ValueError('Registered CF3 atom identities differ')
    point = next(p for p in plan['points'] if p['point_id'] == spec['point_id'])
    center = next(p for p in plan['points'] if p['point_id'] == 'center')
    pins = {p['path']: p for p in plan['accessed_source_fingerprints']}
    for name in ('initial_density_checkpoint', 'old_result', 'old_gradient', 'old_XYZ'):
        path = local(point[name])
        item = pins.get(path.relative_to(ROOT).as_posix())
        if not path.is_file() or path.is_symlink() or not item or sha(path) != item['sha256'] or path.stat().st_size != item['size_bytes']:
            raise ValueError('Old source fingerprint differs: ' + name)
    seed = local(point['initial_density_checkpoint'])
    if sha(seed) != point['initial_density_checkpoint_sha256']:
        raise ValueError('Archived initial density seed differs')
    old = read(local(point['old_result']))
    if old.get('gradient_complete') is not True or old.get('electronic_complete') is not True or old['coordinates_bohr'] != point['coordinates_bohr']:
        raise ValueError('Repeat coordinates do not identify a complete old point')
    if len(point['coordinates_bohr']) != 26 or any(len(row) != 3 or any(not finite(v) for v in row) for row in point['coordinates_bohr']):
        raise ValueError('Invalid full-precision Bohr coordinate array')
    return plan, point, center, budget_path


def parse_last_log(path):
    expression = re.compile(r'(?:Extra cycle\s+|cycle=\s*\d+\s+)E=\s*([-+\deE.]+)\s+delta_E=\s*([-+\deE.]+)\s+\|g\|=\s*([-+\deE.]+)\s+\|ddm\|=\s*([-+\deE.]+)')
    rows = []
    for line in path.read_text('utf-8', errors='replace').splitlines():
        match = expression.search(line)
        if match:
            rows.append({'line': line, 'energy_Eh': float(match[1]), 'delta_energy_Eh': float(match[2]),
                         'orbital_gradient_backend_norm': float(match[3]), 'density_change_norm': float(match[4])})
    return rows[-1] if rows else None


def execute(spec_path, spec, output):
    plan, point, center, budget_path = validate(spec, output)
    output.mkdir(parents=True, exist_ok=False)
    started_epoch, started = time.time(), time.monotonic()
    state = {'schema_version': '1.0', 'scientific_review_status': 'review_required', 'release_eligible': False,
        'stage': spec['stage'], 'point_id': spec['point_id'], 'reservation_id': spec['reservation_id'],
        'status': 'initializing', 'started_epoch': started_epoch, 'started_utc': datetime.now(timezone.utc).isoformat(),
        'global_started_epoch': spec['global_started_epoch'], 'global_deadline_epoch': spec['global_deadline_epoch'],
        'scf_started': False, 'scf_converged': False, 'electronic_complete': False,
        'gradient_started': False, 'gradient_complete': False, 'gradient_reservations': 0, 'nuclear_gradient_calls': 0, 'identity_checks_passed': False,
        'stationary_point_qualified': False,
        'full_Hessian': 'not_performed', 'formal_IRC': 'not_performed', 'coordinates_bohr': point['coordinates_bohr'],
        'species_manifest': plan['species_manifest'], 'worker_sha256': sha(Path(__file__).resolve()),
        'source_spec_sha256': sha(spec_path), 'plan_sha256': PLAN_SHA, 'contract_sha256': spec['contract_sha256'],
        'initial_density_seed_sha256': point['initial_density_checkpoint_sha256']}
    log = None

    def save():
        state['worker_elapsed_seconds'] = time.monotonic() - started
        write(output / 'result.json', state)
        write(output / 'status.json', state)

    def interrupted(signum, frame):
        raise TimeoutError('Worker signal/deadline stop: ' + str(signum))

    def check_identity():
        if sha(PLAN) != PLAN_SHA or sha(CONTRACT) != spec['contract_sha256'] or sha(Path(__file__).resolve()) != spec['expected_worker_sha256']:
            raise RuntimeError('Plan, contract or worker changed during execution')
        if time.time() >= spec['global_deadline_epoch']:
            raise TimeoutError('Cumulative diagnostic deadline reached')
        shared = read(budget_path)
        if shared.get('started_epoch') != spec['global_started_epoch'] or shared.get('deadline_epoch') != spec['global_deadline_epoch']:
            raise RuntimeError('Shared deadline changed during execution')

    save()
    try:
        if os.name != 'posix' or not hasattr(signal, 'SIGALRM'):
            raise RuntimeError('Actual execution requires existing Linux/WSL backend')
        signal.signal(signal.SIGALRM, interrupted); signal.signal(signal.SIGTERM, interrupted)
        signal.signal(signal.SIGINT, interrupted)
        signal.setitimer(signal.ITIMER_REAL, min(480., spec['global_deadline_epoch'] - time.time()))
        os.environ.update(OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', OPENBLAS_NUM_THREADS='1')
        import numpy as np
        import pyscf
        from pyscf import dft, gto, lib
        from pyscf.scf import chkfile, hf
        lib.num_threads(4)
        import inspect
        import platform
        from pyscf.solvent import ddcosmo, _attach_solvent
        from pyscf.dft import rks
        from pyscf.df import df_jk
        source_files = [Path(pyscf.__file__).resolve(), Path(hf.__file__).resolve(),
            Path(rks.__file__).resolve(), Path(ddcosmo.__file__).resolve(),
            Path(_attach_solvent.__file__).resolve(), Path(df_jk.__file__).resolve()]
        state['software_source_fingerprints'] = [{'path': str(p), 'sha256': sha(p), 'size_bytes': p.stat().st_size} for p in source_files]
        kernel_source = inspect.getsource(hf.kernel)
        if 'mf.post_kernel(locals())' not in kernel_source or 'conv_tol_grad = conv_tol_grad * 3' not in kernel_source or 'conv_tol = conv_tol * 10' not in kernel_source:
            raise RuntimeError('Actual backend SCF/extra-cycle/post_kernel implementation requires review')
        (output/'hf-kernel-source.py').write_text(kernel_source, encoding='utf-8')
        state['runtime_environment'] = {'platform': platform.platform(), 'sys_executable': sys.executable,
            'sys_prefix': sys.prefix, 'sys_base_prefix': sys.base_prefix,
            'WSL_DISTRO_NAME': os.environ.get('WSL_DISTRO_NAME'),
            'os_release': Path('/etc/os-release').read_text('utf-8') if Path('/etc/os-release').exists() else None}
        state['software'] = {'python': sys.version, 'numpy': np.__version__, 'pyscf': pyscf.__version__,
            'pyscf_module': str(Path(pyscf.__file__).resolve()), 'threads': lib.num_threads(),
            'TIGHT_GRAD_CONV_TOL': bool(hf.TIGHT_GRAD_CONV_TOL)}
        shutil.copyfile(spec_path, output / 'requested-spec.json')
        shutil.copyfile(Path(__file__).resolve(), output / 'worker_snapshot.py')
        seed = local(point['initial_density_checkpoint'])
        shutil.copyfile(seed, output / 'initial-scf-guess.chk')
        if sha(seed) != point['initial_density_checkpoint_sha256'] or sha(output / 'initial-scf-guess.chk') != point['initial_density_checkpoint_sha256']:
            raise RuntimeError('Seed changed during snapshot')
        coordinates = np.asarray(point['coordinates_bohr'], dtype=float)
        center_coordinates = np.asarray(center['coordinates_bohr'], dtype=float)
        (output / 'input.xyz').write_text('26\nreview_required; Angstrom; full Bohr coordinates in result.json\n' + '\n'.join(
            f'{s} {x:.13f} {y:.13f} {z:.13f}' for s, (x, y, z) in zip(SYMBOLS, coordinates * BOHR_A)) + '\n', encoding='utf-8')
        log = (output / 'pyscf.log').open('w', buffering=1)

        def molecule(coords):
            mol = gto.M(atom=list(zip(SYMBOLS, coords.tolist())), unit='Bohr', basis='def2-svp',
                charge=0, spin=0, symmetry=False, verbose=4, max_memory=4000)
            mol.stdout = log
            return mol

        mol = molecule(coordinates)
        seed_center_mol = molecule(center_coordinates)
        previous, seed_record = chkfile.load_scf(str(output / 'initial-scf-guess.chk'))
        checks = {'symbols': [previous.atom_symbol(i) for i in range(previous.natm)] == SYMBOLS,
            'charges': previous.atom_charges().tolist() == seed_center_mol.atom_charges().tolist(),
            'seed_geometry_is_archived_center': previous.natm == 26 and float(np.max(np.abs(previous.atom_coords() - center_coordinates))) <= 2e-9,
            'charge_spin': previous.charge == seed_center_mol.charge == 0 and previous.spin == seed_center_mol.spin == 0,
            'basis': plain(previous._basis) == plain(seed_center_mol._basis), 'cart': previous.cart == seed_center_mol.cart,
            'AO_labels': previous.ao_labels(fmt=False) == mol.ao_labels(fmt=False), 'AO_count': previous.nao_nr() == mol.nao_nr()}
        if not all(checks.values()):
            write(output / 'checkpoint-validation.json', checks)
            raise RuntimeError('Seed incompatible with archived center/order/basis/state')
        coeff, occ = np.asarray(seed_record['mo_coeff']), np.asarray(seed_record['mo_occ'])
        if coeff.ndim != 2 or occ.ndim != 1 or coeff.shape != (mol.nao_nr(), len(occ)) or not np.all(np.isfinite(coeff)):
            raise RuntimeError('Restricted seed MO dimensions invalid')
        if not np.all(np.isfinite(occ)) or not np.all(np.isclose(occ, 0, rtol=0, atol=1e-12) | np.isclose(occ, 2, rtol=0, atol=1e-12)):
            raise RuntimeError('Seed occupation not restricted closed shell')
        density = hf.make_rdm1(coeff, occ)
        if density.shape != (mol.nao_nr(), mol.nao_nr()) or not np.all(np.isfinite(density)):
            raise RuntimeError('Seed density shape or finiteness invalid')
        electrons = float(np.einsum('ij,ji->', density, seed_center_mol.intor_symmetric('int1e_ovlp')).real)
        checks.update(seed_density_electrons=electrons, expected_electrons=mol.nelectron,
            restricted_occupations=True, electron_count_passed=abs(electrons - mol.nelectron) <= 1e-5 and abs(float(occ.sum()) - mol.nelectron) <= 1e-6,
            role='Archived center density is an initial guess at each displaced geometry; never fresh SCF evidence')
        write(output / 'checkpoint-validation.json', checks)
        if not checks['electron_count_passed']:
            raise RuntimeError('Seed electron count mismatch')
        np.save(output / 'initial-density.npy', density)
        state['initial_density_sha256'] = sha(output / 'initial-density.npy')
        mf = dft.RKS(mol).density_fit()
        mf.xc = 'PBE0'; mf.grids.level = 2
        mf.conv_tol, mf.conv_tol_grad, mf.max_cycle = 1e-12, 1e-10, 120
        mf.chkfile = str(output / 'scf.chk')
        mf = mf.ddCOSMO(); mf.with_solvent.eps = 2.2706
        mf.with_solvent.lmax, mf.with_solvent.lebedev_order = 6, 17
        mf.with_solvent.grids.level = 1
        mf.with_solvent.equilibrium_solvation = True; mf.with_solvent.frozen = False
        state['model'] = {'xc': 'PBE0', 'basis': 'def2-svp', 'method': 'DF-RKS', 'solvent': 'ddCOSMO',
            'epsilon': 2.2706, 'grid_level': 2, 'solvent_grid_level': 1, 'lmax': 6, 'lebedev_order': 17,
            'equilibrium_solvation': True, 'frozen': False, 'scf_conv_tol': mf.conv_tol,
            'scf_conv_tol_grad': mf.conv_tol_grad, 'max_scf_cycles': 120, 'grid_response': True,
            'auxbasis_response': True, 'nuclear_gradient_evaluated': False, 'charge': 0, 'spin': 0, 'additional_D3_D4': False,
            'memory_mb_soft': 4000, 'threads': 4}
        final_scf = {}
        original_post_kernel = mf.post_kernel

        def post_kernel(env):
            original_post_kernel(env)
            final_scf.update({'source': 'hf.kernel post_kernel locals, full precision; no additional evaluation',
                'orbital_gradient_backend_norm': float(env['norm_gorb']), 'density_change_norm': float(env['norm_ddm']),
                'delta_energy_Eh': float(env['e_tot'] - env['last_hf_e']), 'energy_Eh': float(env['e_tot']),
                'scf_convergence_flag_at_post_kernel': bool(env['scf_conv']),
                'backend_effective_final_conv_tol': float(env['conv_tol']),
                'backend_effective_final_conv_tol_grad': float(env['conv_tol_grad']),
                'TIGHT_GRAD_CONV_TOL': bool(hf.TIGHT_GRAD_CONV_TOL)})
            write(output / 'final-scf-diagnostics.json', final_scf)

        def callback(env):
            row = {'cycle_0': int(env.get('cycle', -1)), 'energy_Eh': float(env['e_tot']),
                   'worker_elapsed_seconds': time.monotonic() - started}
            for source_key, key in [('norm_gorb', 'orbital_gradient_backend_norm'), ('norm_ddm', 'density_change_norm')]:
                if source_key in env:
                    row[key] = float(env[source_key])
            with (output / 'electronic-history.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(row, allow_nan=False) + '\n')

        mf.post_kernel = post_kernel; mf.callback = callback
        check_identity()
        state.update(status='scf_started', scf_started=True); save()
        began = time.monotonic()
        energy = mf.kernel(dm0=np.asarray(density).copy())
        state.update(SCF_seconds=time.monotonic() - began, scf_converged=bool(mf.converged))
        log.flush()
        state['final_scf_diagnostics'] = final_scf
        state['final_scf_rounded_log'] = parse_last_log(output / 'pyscf.log')
        if not mf.converged or not np.isfinite(energy):
            raise RuntimeError('Fresh same-model SCF did not converge')
        final_occ = np.asarray(mf.mo_occ)
        if not np.all(np.isfinite(final_occ)) or not np.all(np.isclose(final_occ, 0, rtol=0, atol=1e-12) | np.isclose(final_occ, 2, rtol=0, atol=1e-12)) or abs(float(final_occ.sum()) - mol.nelectron) > 1e-6:
            raise RuntimeError('Final electron number or restricted occupation mismatch')
        if mol.nelectron != 154 or abs(float(final_occ.sum()) - 154) > 1e-6:
            raise RuntimeError('This fixed CF3 center must have exactly 154 electrons')
        enuc = float(mol.energy_nuc()); esolv = float(mf.with_solvent.e)
        state.update(energy_Eh=float(energy), nuclear_repulsion_Eh=enuc, solvent_polarization_Eh=esolv,
            electronic_plus_solvent_excluding_nuclear_Eh=float(energy) - enuc,
            electronic_excluding_solvent_and_nuclear_Eh=float(energy) - enuc - esolv,
            scf_summary=plain(mf.scf_summary), electronic_complete=True,
            energy_partition_convention='Algebraic partition of the observed total; solvent polarization is the backend-observed contribution, included once',
            checkpoint_sha256=sha(output / 'scf.chk'), final_occupations=final_occ.tolist(),
            final_electron_count=float(final_occ.sum()), basis_functions=mol.nao_nr(),
            identity_checks_passed=True,
            status='electronic_complete_terminal_check_pending')
        save(); write(output / 'electronic-result.json', state)
        if not final_scf or any(not finite(final_scf.get(k)) for k in ('orbital_gradient_backend_norm', 'density_change_norm', 'delta_energy_Eh')):
            raise RuntimeError('Full-precision terminal SCF diagnostics missing')
        if True:  # This trial always uses the unchanged strict final electronic criterion
            state['strict_final_orbital_diagnostic_passed'] = final_scf['orbital_gradient_backend_norm'] <= 1e-9
            save()
            if not state['strict_final_orbital_diagnostic_passed']:
                raise RuntimeError('Center final orbital diagnostic failed; trial ended without nuclear gradients')
        check_identity()
        if sha(seed) != point['initial_density_checkpoint_sha256']:
            raise RuntimeError('Archived seed changed during evaluation')
        state.update(status='completed_center_electronic_check_passed', center_electronic_check_passed=True, process_intended_returncode=0)
        returncode = 0
    except BaseException as exc:
        state.update(status='failed', error=repr(exc), process_intended_returncode=1)
        (output / 'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        returncode = 1
    finally:
        if hasattr(signal, 'setitimer'):
            signal.setitimer(signal.ITIMER_REAL, 0)
        if log is not None:
            log.flush(); log.close()
        state['finished_epoch'] = time.time(); state['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save()
    print(json.dumps({'output': str(output), 'status': state['status'], 'stage': spec['stage'],
        'point_id': spec['point_id'], 'gradient_complete': state['gradient_complete'],
        'returncode': returncode}, ensure_ascii=False), flush=True)
    return returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--validate-only', action='store_true', help='No backend import and no output write')
    args = parser.parse_args()
    spec_path = args.spec.resolve(strict=True)
    spec = read(spec_path); output = args.output.resolve()
    validate(spec, output, require_live=not args.validate_only)
    if args.validate_only:
        print(json.dumps({'entry_validation': 'passed', 'new_quantum_calls': 0, 'output_created': False}))
        return 0
    return execute(spec_path, spec, output)


if __name__ == '__main__':
    sys.exit(main())
