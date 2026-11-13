"""Prepare the one-call SCF-only entry by a checked minimal old-worker diff."""
from datetime import datetime, timezone
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE.parent/'cf3-point-diagnosis-execution-20261113-v1'
PLAN = HERE.parent/'cf3-curvature-diagnosis-20261113-v1/planned-inputs.v2.json'
RAW = ROOT/'scratch/m0-cf3-center-terminal-scf-20261113-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')


def main():
    if (HERE/'worker_scf.py').exists() or (HERE/'contract.v1.json').exists() or RAW.exists():
        raise FileExistsError('Review existing state; a stopped/existing trial cannot be bypassed')
    source = OLD/'worker_point.py'
    if sha(source) != '1ae403af2b963fccd922093dd3d5abeda0153c0f4c76d4e4b11ce57e10b5c1ad':
        raise RuntimeError('Previous reviewed worker changed')
    old = source.read_text('utf-8')
    text = old
    replacements = [
        ('Exactly one reserved, fixed-M0 CF3 E/g evaluation; no optimizer or Hessian.', 'Exactly one reserved, fixed-M0 CF3 center SCF; no nuclear derivative entry.'),
        ('ledger and reserves both SCF and gradient before spawning this worker.', 'ledger and reserves one SCF and zero nuclear gradients before spawning this worker.'),
        ("CONTRACT = PLAN.parent / 'contract.v1.json'", "CONTRACT = HERE / 'contract.v1.json'"),
        ("CONTRACT_SHA = 'bf4f20191070c6072aef98ef6c34fac6413b40cd538d99a4778a614f950e45cc'\n", ''),
        ("POINTS = ['center', 'C6-y-plus', 'C6-y-minus', 'C10-y-plus', 'C10-y-minus']", "POINTS = ['center']"),
        ("if spec.get('stage') not in ('A', 'B') or spec.get('point_id') not in POINTS:", "if spec.get('stage') != 'CENTER_SCF_ONLY' or spec.get('point_id') != 'center':"),
        ("Only the two stages and five fixed CF3 points are accepted", "Only this single fixed CF3 center SCF trial is accepted"),
        ("if local(spec.get('contract_path', '')) != CONTRACT or spec.get('contract_sha256') != CONTRACT_SHA or sha(CONTRACT) != CONTRACT_SHA:", "if local(spec.get('contract_path', '')) != CONTRACT or spec.get('contract_sha256') != sha(CONTRACT):"),
        ("not 1 <= reservation <= 10", "reservation != 1"),
        ("<= 5400.000001", "<= 600.000001"),
        ("('contract_sha256', CONTRACT_SHA)", "('contract_sha256', spec['contract_sha256'])"),
        ("if not 1 <= budget.get('total_scf_attempts', 0) <= 10 or not 1 <= budget.get('gradient_reservations', 0) <= 10:", "if budget.get('total_scf_attempts') != 1 or budget.get('gradient_reservations') != 0 or budget.get('gradient_started') != 0 or budget.get('completed_gradients') != 0:"),
        ("'plan_sha256': PLAN_SHA, 'contract_sha256': CONTRACT_SHA,", "'plan_sha256': PLAN_SHA, 'contract_sha256': spec['contract_sha256'],"),
        ("sha(CONTRACT) != CONTRACT_SHA", "sha(CONTRACT) != spec['contract_sha256']"),
        ("mf.conv_tol, mf.conv_tol_grad, mf.max_cycle = (1e-10, 1e-7, 120) if spec['stage'] == 'A' else (1e-12, 1e-9, 120)", "mf.conv_tol, mf.conv_tol_grad, mf.max_cycle = 1e-12, 1e-10, 120"),
        ("'auxbasis_response': True, 'charge': 0", "'auxbasis_response': True, 'nuclear_gradient_evaluated': False, 'charge': 0"),
        ("'gradient_started': False, 'gradient_complete': False, 'identity_checks_passed': False,", "'gradient_started': False, 'gradient_complete': False, 'gradient_reservations': 0, 'nuclear_gradient_calls': 0, 'identity_checks_passed': False,"),
        ("status='electronic_complete_gradient_pending'", "status='electronic_complete_terminal_check_pending'"),
        ("if spec['stage'] == 'B':", "if True:  # This trial always uses the unchanged strict final electronic criterion"),
        ("Tight-SCF final orbital diagnostic failed; no extra cycles or gradient", "Center final orbital diagnostic failed; trial ended without nuclear gradients"),
    ]
    for old_fragment, new_fragment in replacements:
        if text.count(old_fragment) != 1:
            raise RuntimeError('Unexpected old worker structure: '+old_fragment[:100])
        text = text.replace(old_fragment, new_fragment, 1)
    start = text.index('        check_identity()\n        grad = mf.nuc_grad_method()')
    end = text.index('        check_identity()\n        if sha(seed)', start)
    text = text[:start] + text[end:]
    text = text.replace("state.update(status='completed', process_intended_returncode=0)", "state.update(status='completed_center_electronic_check_passed', center_electronic_check_passed=True, process_intended_returncode=0)")
    marker = "    plan = read(PLAN)\n"
    insertion = """    contract = read(CONTRACT)
    required_limits = {'shared_wall_seconds': 600, 'per_point_wall_seconds': 480,
        'max_SCF_attempts': 1, 'max_gradient_reservations': 0, 'max_workers': 1,
        'threads_per_worker': 4, 'memory_mb_soft_per_worker': 4000, 'max_SCF_cycles_per_point': 120}
    if contract.get('limits') != required_limits or contract.get('internal_targets') != {'conv_tol': 1e-12, 'conv_tol_grad': 1e-10} or contract.get('final_orbital_norm_max') != 1e-9:
        raise ValueError('Unexpected fixed SCF-only contract')
"""
    if text.count(marker) != 1:
        raise RuntimeError('Unexpected plan validation marker')
    text = text.replace(marker, insertion+marker, 1)
    marker = "        lib.num_threads(4)\n"
    insertion = """        import inspect
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
"""
    text = text.replace(marker, marker+insertion, 1)
    marker = "        enuc = float(mol.energy_nuc()); esolv = float(mf.with_solvent.e)\n"
    text = text.replace(marker, "        if mol.nelectron != 154 or abs(float(final_occ.sum()) - 154) > 1e-6:\n            raise RuntimeError('This fixed CF3 center must have exactly 154 electrons')\n"+marker, 1)
    tree = ast.parse(text)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'kernel']
    if len(calls) != 1 or any(isinstance(n, ast.Attribute) and n.attr == 'nuc_grad_method' for n in ast.walk(tree)):
        raise RuntimeError('SCF-only AST boundary failed')
    with (HERE/'worker_scf.py').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    with (HERE/'worker-from-prior.diff').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(''.join(difflib.unified_diff(old.splitlines(True), text.splitlines(True), fromfile='sealed-prior-worker', tofile='SCF-only-worker')))
    prior = json.loads((OLD/'results-v1/summary.json').read_bytes())
    baseline = prior['resources']['historical_plus_recorded_new_worker_hours_lower_bound']
    if baseline < 20.51079460605307:
        raise RuntimeError('Resource history would be rolled back')
    plan = json.loads(PLAN.read_bytes())
    center = next(p for p in plan['points'] if p['point_id']=='center')
    contract = {'schema_version': '1.0', 'task_id': 'A01-M0-CF3-CENTER-TERMINAL-SCF-20261113-v1',
        'created_utc': datetime.now(timezone.utc).isoformat(), 'scientific_review_status': 'review_required',
        'release_eligible': False, 'scope': 'One original CF3 center SCF only; normal extra-cycle retained; zero nuclear gradients',
        'limits': {'shared_wall_seconds': 600, 'per_point_wall_seconds': 480, 'max_SCF_attempts': 1,
            'max_gradient_reservations': 0, 'max_workers': 1, 'threads_per_worker': 4,
            'memory_mb_soft_per_worker': 4000, 'max_SCF_cycles_per_point': 120},
        'internal_targets': {'conv_tol': 1e-12, 'conv_tol_grad': 1e-10}, 'final_orbital_norm_max': 1e-9,
        'historical_recorded_worker_hours_lower_bound': baseline,
        'normal_extra_cycle': True, 'no_changed_PySCF_convergence_function': True,
        'no_new_energy_or_density_acceptance_threshold': True,
        'no_retry_extension_parameter_change_or_followup_quantum': True,
        'fixed_model': {'method': 'DF-RKS', 'xc': 'PBE0', 'basis': 'def2-svp', 'solvent': 'ddCOSMO',
            'epsilon': 2.2706, 'grid_level': 2, 'solvent_grid_level': 1, 'lmax': 6,
            'lebedev_order': 17, 'equilibrium_solvation': True, 'frozen': False,
            'charge': 0, 'spin': 0, 'electrons': 154},
        'center': center, 'species_manifest': plan['species_manifest'],
        'plan_source': PLAN.relative_to(ROOT).as_posix(), 'plan_sha256': sha(PLAN),
        'worker_sha256': sha(HERE/'worker_scf.py'), 'previous_worker_sha256': sha(source),
        'execution_commit': None, 'execution_identity': 'Archived code and input fingerprints; later publication commit is not the execution commit',
        'previous_background': {'B_main_cycle4_orbital_norm': 9.689037768617906e-10,
            'B_terminal_orbital_norm': 1.6225317681152e-9,
            'A_reciprocal_difference_Eh_bohr2': .0014988911403202325,
            'B_nuclear_gradient': 'not_started', 'cause': 'unknown'},
        'scientific_boundary': 'Passing center electronic check is not complete curvature, Hessian, spectrum, barrier, mechanism or experimental validation'}
    save(HERE/'contract.v1.json', contract)
    save(HERE/'preparation.v1.json', {'new_quantum_calls': 0, 'status': 'PREPARED_NOT_EXECUTED',
        'worker_sha256': sha(HERE/'worker_scf.py'), 'contract_sha256': sha(HERE/'contract.v1.json'),
        'AST_SCF_kernel_calls': len(calls), 'AST_nuclear_gradient_method_references': 0,
        'history_lower_bound': baseline})
    print(json.dumps({'worker_sha256': sha(HERE/'worker_scf.py'), 'contract_sha256': sha(HERE/'contract.v1.json'),
        'history_lower_bound': baseline, 'new_quantum_calls': 0}))


if __name__ == '__main__':
    main()
