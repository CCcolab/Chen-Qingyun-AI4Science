"""Saved-data-only analysis of the same-M0 CF3 tight-SCF five-point diagnosis.

No electronic-structure import, child process, network call or new derivative.
Two sampled columns never constitute a full Hessian or minimum qualification.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD_PREPARED = HERE.parent / 'cf3-curvature-diagnosis-20261113-v1'
OLD_RAW = ROOT / 'scratch/m0-cf3-point-diagnosis-20261113-v1'
RAW = ROOT / 'scratch/m0-cf3-tight-gradient-diagnosis-20261113-v1'
HISTORY = 20.55026662453337
IDS = ['center', 'C6-y-plus', 'C6-y-minus', 'C10-y-plus', 'C10-y-minus']
COLS = [(16, 'C6-y'), (28, 'C10-y')]
H = 0.0005


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def first(mapping, *keys):
    return next((mapping[key] for key in keys if key in mapping), None)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def local(value):
    text = str(value)
    if sys.platform == 'win32' and text.startswith('/mnt/') and len(text) > 7 and text[6] == '/':
        text = text[5].upper() + ':/' + text[7:]
    elif sys.platform != 'win32' and len(text) > 2 and text[1] == ':' and text[2] in '/\\':
        text = '/mnt/' + text[0].lower() + '/' + text[3:].replace('\\', '/')
    path = Path(text)
    path = path if path.is_absolute() else ROOT / path
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(ROOT.resolve()) or not resolved.is_file() or path.is_symlink():
        raise ValueError('Expected a regular in-project evidence file: ' + str(path))
    return resolved


class Reader:
    def __init__(self):
        self.pins, self.issues = {}, []

    def pin(self, path, expected=None):
        path = local(path)
        name = path.relative_to(ROOT).as_posix()
        item = {'path': name, 'sha256': digest(path), 'size_bytes': path.stat().st_size}
        if expected is not None and item['sha256'] != expected:
            raise ValueError('Recorded source SHA mismatch: ' + name)
        if name in self.pins and self.pins[name] != item:
            raise ValueError('Source changed between reads: ' + name)
        self.pins[name] = item
        return path

    def json(self, path):
        return json.loads(self.pin(path).read_bytes())

    def array(self, path, expected=None):
        value = np.load(self.pin(path, expected), allow_pickle=False)
        if value.shape != (26, 3) or not np.all(np.isfinite(value)):
            raise ValueError('Expected finite saved 26x3 nuclear gradient')
        return value

    def unchanged(self):
        return [name for name, item in self.pins.items()
                if not (ROOT / name).is_file() or digest(ROOT / name) != item['sha256']
                or (ROOT / name).stat().st_size != item['size_bytes']]


def stage_columns(rows, gradients):
    result = {'scope': 'Two sampled columns only; not a full Hessian', 'h_bohr': H,
              'columns': {}, 'mutual_pair': None,
              'full_relative_Frobenius_residual': None,
              'full_curvature_qualification': 'not_awarded',
              'frequencies_computed': False, 'imaginary_frequency_count': None}
    for column, prefix in COLS:
        plus, minus = prefix + '-plus', prefix + '-minus'
        if plus not in gradients or minus not in gradients:
            result['columns'][str(column)] = {'state': 'not_available',
                'reason': 'Two complete qualified saved endpoint gradients required'}
            continue
        vector = ((gradients[plus] - gradients[minus]) / (2 * H)).ravel()
        row = {'state': 'complete_sampled_column', 'coordinate_0': column,
               'column_Eh_bohr2': vector.tolist(), 'diagonal_Eh_bohr2': float(vector[column]),
               'plus_point': plus, 'minus_point': minus,
               'energy_FD_first': None, 'energy_FD_second_diagonal': None}
        if 'center' in gradients:
            E0, Ep, Em = (rows[key]['energy_Eh'] for key in ('center', plus, minus))
            fd1 = (Ep - Em) / (2 * H)
            analytic = float(gradients['center'].ravel()[column])
            tol1 = 5e-6 + 5e-4 * abs(fd1)
            fd2 = (Ep + Em - 2 * E0) / (H * H)
            tol2 = 1e-4 + 1e-3 * abs(float(vector[column]))
            row['energy_FD_first'] = {'finite_difference_Eh_bohr': fd1,
                'center_gradient_Eh_bohr': analytic, 'absolute_residual_Eh_bohr': abs(fd1 - analytic),
                'tolerance_Eh_bohr': tol1, 'passed': abs(fd1 - analytic) <= tol1}
            row['energy_FD_second_diagonal'] = {'finite_difference_Eh_bohr2': fd2,
                'gradient_H_diagonal_Eh_bohr2': float(vector[column]),
                'absolute_residual_Eh_bohr2': abs(fd2 - vector[column]),
                'tolerance_Eh_bohr2': tol2, 'passed': bool(abs(fd2 - vector[column]) <= tol2),
                'role': 'Diagnostic only; not a qualification gate'}
        result['columns'][str(column)] = row
    a, b = result['columns']['16'], result['columns']['28']
    if a['state'] == b['state'] == 'complete_sampled_column':
        h28_16, h16_28 = a['column_Eh_bohr2'][28], b['column_Eh_bohr2'][16]
        difference = h28_16 - h16_28
        result['mutual_pair'] = {'H_28_16_Eh_bohr2': h28_16, 'H_16_28_Eh_bohr2': h16_28,
            'signed_antisymmetry_Eh_bohr2': difference,
            'absolute_antisymmetry_Eh_bohr2': abs(difference),
            'original_absolute_threshold_Eh_bohr2': 1e-4,
            'within_original_threshold_for_this_pair_only': abs(difference) <= 1e-4,
            'not_a_complete_Hessian_test': True}
    return result


def process_for(reader, raw, point_id, controller):
    for name in (point_id, 'TIGHT_GRADIENT-' + point_id, 'TIGHT-' + point_id):
        path = raw / 'processes' / (name + '.json')
        if path.is_file():
            return reader.json(path)
    return next((p for p in controller.get('processes', [])
                 if isinstance(p, dict) and p.get('point_id') == point_id), None)


def load_point(reader, raw, point, controller):
    point_id = point['point_id']
    process = process_for(reader, raw, point_id, controller)
    folder = raw / 'points' / point_id
    if process and process.get('result_path'):
        try:
            result_path = local(process['result_path'])
            folder = result_path.parent
        except (OSError, ValueError):
            result_path = folder / 'result.json'
    else:
        result_path = folder / 'result.json'
    row = {'point_id': point_id, 'stage': 'TIGHT_GRADIENT', 'process': process,
        'execution_state': 'NOT_EXECUTED' if process is None and not result_path.is_file() else 'incomplete_or_failed',
        'worker_result_available': result_path.is_file(), 'raw_complete': False,
        'qualified_point': False, 'identity_checks': {}, 'returncode': None,
        'energy_Eh': None, 'actual_final_orbital_norm': None,
        'gradient_atom_norm_max_Eh_bohr': None, 'gradient_atom_norm_rms_Eh_bohr': None}
    if not result_path.is_file():
        return row, None
    try:
        result = reader.json(result_path)
        row['worker_result'] = result
        if process and process.get('worker_result_sha256'):
            reader.pin(result_path, process['worker_result_sha256'])
        row.update(returncode=first(process or {}, 'returncode', 'return_code', 'exit_code'),
            timed_out=first(process or {}, 'timed_out', 'timeout'),
            external_stop=(process or {}).get('external_stop'),
            SCF_converged=result.get('scf_converged'),
            electronic_complete=result.get('electronic_complete'),
            gradient_complete_flag=result.get('gradient_complete'),
            energy_Eh=first(result, 'energy_Eh', 'total_energy_Eh'),
            worker_status=result.get('status'), failure=first(result, 'failure', 'error'))
        diagnostics = result.get('final_scf_diagnostics') or {}
        norm = first(diagnostics, 'orbital_gradient_backend_norm', 'orbital_gradient_norm', 'norm_gorb')
        row['actual_final_orbital_norm'] = norm
        row['final_SCF_residuals'] = diagnostics
        row['strict_final_orbital_norm_passed'] = norm <= 1e-9 if finite(norm) else None
        coords = np.asarray(result.get('coordinates_bohr', []), dtype=float)
        expected = np.asarray(point['coordinates_bohr'], dtype=float)
        error = float(np.max(np.abs(coords - expected))) if coords.shape == expected.shape == (26, 3) else None
        row['maximum_coordinate_difference_from_planned_bohr'] = error
        row['identity_checks'] = {'exact_planned_geometry': error is not None and error <= 1e-12,
            'worker_identity_checks_passed': result.get('identity_checks_passed') is True,
            'initial_seed_SHA_matches_plan': result.get('initial_density_seed_sha256') == point['initial_density_checkpoint_sha256'],
            'point_id': result.get('point_id') == point_id,
            'stage': result.get('stage') == 'TIGHT_GRADIENT',
            'electron_count': result.get('final_electron_count') == 154,
            'basis_functions': result.get('basis_functions') == 319,
            'worker_code_SHA': result.get('worker_sha256') == digest(HERE / 'worker_points.py'),
            'contract_SHA': result.get('contract_sha256') == digest(HERE / 'contract.v1.json'),
            'inputs_SHA': result.get('inputs_sha256') == digest(HERE / 'inputs.v1.json')}
        model = result.get('model') or {}
        fixed_model = {'xc': 'PBE0', 'basis': 'def2-svp', 'method': 'DF-RKS',
            'solvent': 'ddCOSMO', 'epsilon': 2.2706, 'grid_level': 2,
            'solvent_grid_level': 1, 'lmax': 6, 'lebedev_order': 17,
            'equilibrium_solvation': True, 'frozen': False,
            'scf_conv_tol': 1e-12, 'scf_conv_tol_grad': 1e-10,
            'max_scf_cycles': 120, 'charge': 0, 'spin': 0,
            'grid_response': True, 'auxbasis_response': True, 'additional_D3_D4': False}
        row['identity_checks']['fixed_model_and_tight_SCF'] = all(model.get(k) == v for k, v in fixed_model.items())
        response = result.get('gradient_response') or {}
        row['identity_checks']['saved_gradient_response'] = all(response.get(k) == v for k, v in
            {'grid_response': True, 'auxbasis_response': True, 'equilibrium_solvation': True, 'frozen': False}.items())
        row['identity_checks']['backend_orbital_norm_convention'] = diagnostics.get('TIGHT_GRAD_CONV_TOL') is True
        spec_path = raw / 'specs' / (point_id + '.json')
        if spec_path.is_file():
            reader.pin(spec_path, result.get('source_spec_sha256'))
        row['identity_checks']['spec_SHA_recorded_and_available'] = (
            spec_path.is_file() and isinstance(result.get('source_spec_sha256'), str))
        if not (result.get('gradient_complete') is True and result.get('scf_converged') is True
                and finite(row['energy_Eh'])):
            return row, None
        gradient_path = next((folder / name for name in ('g.npy', 'gradient.npy') if (folder / name).is_file()), None)
        gradient_sha = first(result, 'gradient_npy_sha256', 'g_npy_sha256', 'gradient_sha256')
        if gradient_path is None or not isinstance(gradient_sha, str):
            raise ValueError('Complete gradient lacks NPY evidence/fingerprint')
        g = reader.array(gradient_path, gradient_sha)
        if 'gradient_Eh_per_bohr' in result:
            json_g = np.asarray(result['gradient_Eh_per_bohr'], dtype=float)
            if json_g.shape != g.shape or not np.array_equal(json_g, g):
                raise ValueError('Saved JSON and NPY gradients differ')
        norms = np.linalg.norm(g, axis=1)
        row.update(raw_complete=True, gradient_atom_norm_max_Eh_bohr=float(norms.max()),
            gradient_atom_norm_rms_Eh_bohr=float(np.sqrt(np.mean(norms ** 2))),
            gradient_cartesian_component_max_Eh_bohr=float(np.max(np.abs(g))),
            gradient_cartesian_component_rms_Eh_bohr=float(np.sqrt(np.mean(g ** 2))))
        row['center_raw_gradient_gate_passed'] = (row['gradient_atom_norm_rms_Eh_bohr'] <= 3e-4
            and row['gradient_atom_norm_max_Eh_bohr'] <= 4.5e-4) if point_id == 'center' else None
        row['qualified_point'] = (all(row['identity_checks'].values())
            and result.get('electronic_complete') is True and row['strict_final_orbital_norm_passed'] is True
            and row['returncode'] == 0 and row['timed_out'] is False and row['external_stop'] is False
            and (point_id != 'center' or row['center_raw_gradient_gate_passed'] is True))
        row['execution_state'] = 'complete_qualified_diagnostic_point' if row['qualified_point'] else 'complete_raw_unqualified_point'
        return row, g if row['qualified_point'] else None
    except Exception as exc:
        reader.issues.append({'path': str(result_path), 'issue': repr(exc)})
        row['read_issue'] = repr(exc)
        return row, None


def load_baseline(reader, plan, stage):
    rows, gradients = {}, {}
    for point in plan['points']:
        point_id = point['point_id']
        if stage == 'A':
            folder = OLD_RAW / 'points' / ('A-' + point_id)
            result_path, gradient_path = folder / 'result.json', folder / 'gradient.npy'
        else:
            result_path, gradient_path = local(point['old_result']), local(point['old_gradient'])
        row = reader.json(result_path)
        rows[point_id] = row
        gradients[point_id] = reader.array(gradient_path, row.get('gradient_npy_sha256'))
        if not (row.get('scf_converged') is True and row.get('gradient_complete') is True
                and np.max(np.abs(np.asarray(row['coordinates_bohr']) - np.asarray(point['coordinates_bohr']))) <= 1e-12):
            raise ValueError('Old baseline point incomplete/identity mismatch: ' + stage + '/' + point_id)
        if stage == 'A' and row.get('initial_density_seed_sha256') != point['initial_density_checkpoint_sha256']:
            raise ValueError('Old A does not identify the same archived density seed: ' + point_id)
    return rows, gradients, stage_columns(rows, gradients)


def resource_audit(budget, points, controller):
    aliases = {'SCF_attempts': ('total_scf_attempts', 'SCF_attempts'),
        'SCF_started': ('SCF_started', 'scf_started'),
        'gradient_reservations': ('gradient_reservations',),
        'gradient_started': ('gradient_started',), 'gradient_complete': ('completed_gradients',)}
    scalars = {key: first(budget, *names) for key, names in aliases.items()}
    events = budget.get('events')
    checks, counts = {}, None
    if isinstance(events, list):
        counts = dict(Counter(event.get('event') for event in events))
        groups = {'SCF_attempts': {'reserve', 'reserved'}, 'gradient_reservations': {'reserve', 'reserved'},
            'SCF_started': {'SCF_started', 'scf_started'}, 'gradient_started': {'gradient_started', 'gradient_start'},
            'gradient_complete': {'gradient_completed', 'gradient_complete'}}
        for key, labels in groups.items():
            checks[key + '_events_match_scalar'] = (sum(e.get('event') in labels for e in events) == scalars[key]
                if scalars[key] is not None else None)
        reserved = [e for e in events if e.get('event') in {'reserve', 'reserved'}]
        ids = [first(e, 'reservation_id', 'reservation') for e in reserved]
        checks['reservations_unique_and_contiguous'] = ids == list(range(1, len(ids) + 1))
        epochs = [first(e, 'epoch', 'timestamp_epoch') for e in events]
        checks['event_epochs_monotone'] = all(finite(v) for v in epochs) and epochs == sorted(epochs)
    processes = [row['process'] for row in points if row['process'] is not None]
    complete = sum(row['raw_complete'] for row in points)
    checks['process_count_matches_reserved_SCF'] = len(processes) == scalars['SCF_attempts'] if scalars['SCF_attempts'] is not None else None
    checks['complete_gradients_match_scalar'] = complete == scalars['gradient_complete'] if scalars['gradient_complete'] is not None else None
    for scalar, flag in [('SCF_started', 'scf_started'), ('gradient_started', 'gradient_started')]:
        flags = [row.get('worker_result', {}).get(flag) for row in points if row['process'] is not None]
        checks[scalar + '_flags_match_scalar'] = (sum(v is True for v in flags) == scalars[scalar]
            if scalars[scalar] is not None and all(v is not None for v in flags) else None)
    durations, intervals = [], []
    for process in processes:
        elapsed = first(process, 'elapsed_seconds', 'worker_elapsed_seconds')
        start, end = first(process, 'started_epoch', 'start_epoch'), first(process, 'finished_epoch', 'finish_epoch')
        if finite(elapsed) and elapsed >= 0:
            durations.append(elapsed)
        if finite(start) and finite(end) and end >= start:
            intervals.append((start, end))
    total = sum(durations) if len(durations) == len(processes) else None
    declared = controller.get('workers_elapsed_seconds')
    checks['worker_elapsed_matches_controller'] = abs(total - declared) <= 1e-6 if finite(total) and finite(declared) else None
    union = None
    if intervals and len(intervals) == len(processes):
        union, (left, right) = 0.0, sorted(intervals)[0]
        for begin, end in sorted(intervals)[1:]:
            if begin <= right:
                right = max(right, end)
            else:
                union += right - left
                left, right = begin, end
        union += right - left
    issues = [key for key, value in checks.items() if value is False]
    return {'scalar_counters': scalars, 'event_counts': counts, 'checks': checks, 'issues': issues,
        'executed_process_count': len(processes), 'complete_gradient_point_count': complete,
        'qualified_diagnostic_point_count': sum(row['qualified_point'] for row in points),
        'new_recorded_worker_elapsed_seconds': total,
        'new_recorded_worker_elapsed_hours': total / 3600 if finite(total) else None,
        'worker_activity_wall_union_seconds': union,
        'first_to_last_worker_wall_span_seconds': max(e for s, e in intervals) - min(s for s, e in intervals) if intervals else None,
        'historical_recorded_worker_hours_lower_bound': HISTORY,
        'historical_plus_recorded_new_worker_hours_lower_bound': HISTORY + total / 3600 if finite(total) else None,
        'complete_historical_worker_or_CPU_hours': None,
        'cost_boundary': 'Failed/timeout processes charged; worker elapsed is not CPU time; planned budget is not consumption'}


def compare(old_rows, old_g, old_columns, rows, gradients, new_columns):
    points = {}
    for point_id in IDS:
        if point_id in gradients:
            points[point_id] = {'tight_minus_A_energy_Eh': rows[point_id]['energy_Eh'] - old_rows[point_id]['energy_Eh'],
                'max_tight_minus_A_gradient_component_Eh_bohr': float(np.max(np.abs(gradients[point_id] - old_g[point_id]))),
                'tight_minus_A_gradient_Frobenius_norm_Eh_bohr': float(np.linalg.norm(gradients[point_id] - old_g[point_id]))}
        else:
            points[point_id] = None
    full_five = len(gradients) == 5 and all(row['qualified_point'] for row in rows.values())
    result = {'all_five_points_qualified': full_five, 'point_differences': points,
        'reciprocal_comparison_eligible': full_five, 'change_in_signed_reciprocal_difference_Eh_bohr2': None,
        'change_in_absolute_reciprocal_difference_Eh_bohr2': None,
        'absolute_change_in_signed_reciprocal_difference_Eh_bohr2': None,
        'remaining_fraction_of_A_absolute_reciprocal_difference': None,
        'same_input_repetition_gradient_bound_Eh_bohr': 1e-8,
        'same_input_pair_difference_comparison_scale_Eh_bohr2': 4e-5,
        'comparison_scale_role': 'Deterministic comparison scale from 4*1e-8/(2h); neither statistical significance nor relaxed qualification',
        'SCF_precision_effect': 'unknown_incomplete_or_unqualified_five_point_evidence',
        'root_cause': 'not_established', 'full_curvature_qualification': 'not_awarded'}
    if full_five and new_columns['mutual_pair'] is not None:
        old, new = old_columns['mutual_pair'], new_columns['mutual_pair']
        signed_change = new['signed_antisymmetry_Eh_bohr2'] - old['signed_antisymmetry_Eh_bohr2']
        result.update(change_in_signed_reciprocal_difference_Eh_bohr2=signed_change,
            absolute_change_in_signed_reciprocal_difference_Eh_bohr2=abs(signed_change),
            change_in_absolute_reciprocal_difference_Eh_bohr2=new['absolute_antisymmetry_Eh_bohr2'] - old['absolute_antisymmetry_Eh_bohr2'],
            remaining_fraction_of_A_absolute_reciprocal_difference=new['absolute_antisymmetry_Eh_bohr2'] / old['absolute_antisymmetry_Eh_bohr2'])
        result['SCF_precision_effect'] = ('sampled_reciprocal_difference_changes_beyond_declared_comparison_scale'
            if abs(signed_change) > 4e-5 else 'no_resolved_change_at_declared_comparison_scale_does_not_exclude_SCF_effects')
    return result


def fmt(value):
    return f'{value:.12g}' if finite(value) else '未知／未取得'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, default=RAW)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--output', type=Path, default=HERE / 'results-v1')
    parser.add_argument('--public-output', type=Path, default=HERE / 'public-summary.v1.json')
    args = parser.parse_args()
    if args.output.exists() or args.public_output.exists():
        raise FileExistsError('Fresh analysis and public-summary paths required; no overwrite')
    reader = Reader()
    raw = args.raw.resolve(strict=True)
    if not raw.is_relative_to(ROOT.resolve()):
        raise ValueError('Saved raw evidence must be in the project')
    controller = reader.json(raw / 'controller-result.json')
    if controller.get('status') in {'running', 'initializing', 'prepared', 'queued'}:
        raise ValueError('Terminal controller evidence required')
    native_launch = reader.json(raw / 'native-launch-result.json') if (raw / 'native-launch-result.json').is_file() else None
    old_plan = reader.json(OLD_PREPARED / 'planned-inputs.v2.json')
    if args.plan:
        new_plan_path = args.plan
    else:
        candidates = sorted(HERE.glob('planned-inputs*.json')) + sorted(HERE.glob('inputs.v*.json'))
        if len(candidates) != 1:
            raise ValueError('Supply --plan if exactly one new planned-inputs JSON is unavailable')
        new_plan_path = candidates[0]
    new_plan = reader.json(new_plan_path)
    contract_path = reader.pin(new_plan.get('contract', HERE / 'contract.v1.json'), new_plan.get('contract_sha256'))
    contract = reader.json(contract_path)
    reader.pin(new_plan_path, contract['inputs_sha256'])
    reader.pin(OLD_PREPARED / 'planned-inputs.v2.json', contract['source_plan_sha256'])
    planned = {point['point_id']: point for point in new_plan['points']}
    if set(planned) != set(IDS):
        raise ValueError('New plan must contain exactly the specified same-M0 five points')
    old_planned = {point['point_id']: point for point in old_plan['points']}
    for point_id in IDS:
        a, b = planned[point_id], old_planned[point_id]
        if (np.asarray(a['coordinates_bohr']).shape != (26, 3)
                or not np.array_equal(np.asarray(a['coordinates_bohr']), np.asarray(b['coordinates_bohr']))
                or a['initial_density_checkpoint_sha256'] != b['initial_density_checkpoint_sha256']):
            raise ValueError('New-vs-A coordinate/seed identity changed: ' + point_id)
    budget = reader.json(raw / 'shared-budget.json')
    rows, gradients = {}, {}
    for point_id in IDS:
        row, gradient = load_point(reader, raw, planned[point_id], controller)
        rows[point_id] = row
        if gradient is not None:
            gradients[point_id] = gradient
    old_rows, old_g, old_columns = load_baseline(reader, old_plan, 'A')
    _, _, original_columns = load_baseline(reader, old_plan, 'v3')
    new_columns = stage_columns(rows, gradients)
    comparison = compare(old_rows, old_g, old_columns, rows, gradients, new_columns)
    resources = resource_audit(budget, list(rows.values()), controller)
    for path in HERE.glob('*.py'):
        reader.pin(path)
    changed = reader.unchanged()
    qualifications = {'CH3_previous_full_curvature_result': 'retained_without_new_calculation',
        'CF3_full_curvature_qualification': 'not_awarded',
        'new_full_Hessian_available': False, 'full_relative_Frobenius_residual': None,
        'new_frequencies_available': False, 'imaginary_frequency_count': None,
        'CF3_local_minimum_qualified': False, 'saddle_or_IRC_run': False,
        'barrier_or_mechanism_claim': False, 'root_cause_established': False,
        'original_full_absolute_threshold_Eh_bohr2': 1e-4,
        'original_full_relative_Frobenius_threshold': .001,
        'center_gradient_pass_does_not_award_minimum_qualification': True}
    def actual_utc(epoch):
        return datetime.fromtimestamp(epoch, timezone.utc).isoformat() if finite(epoch) else None
    started = controller.get('started_epoch')
    run_id = controller.get('run_id')
    derived_run_id = run_id is None
    if run_id is None and finite(started):
        run_id = contract['task_id'] + '@' + str(started)
    common = {'schema_version': '1.0', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'task_id': contract['task_id'], 'run_id': run_id,
        'run_id_role': 'derived_from_task_id_and_recorded_controller_start_epoch' if derived_run_id else 'recorded_controller_run_id',
        'started_epoch': started, 'finished_epoch': controller.get('finished_epoch'),
        'started_utc': actual_utc(started), 'finished_utc': actual_utc(controller.get('finished_epoch')),
        'parameters': {'conv_tol': 1e-12, 'conv_tol_grad': 1e-10, 'max_scf_cycles': 120,
            'actual_final_orbital_norm_max': 1e-9, 'normal_extra_cycle': True, 'h_bohr': H,
            'SCF_energy_or_density_change_new_acceptance_gate': False},
        'execution_commit': None, 'scientific_review_status': 'review_required', 'release_eligible': False,
        'scope': 'Same M0 CF3, center plus C6-y/C10-y +/-0.0005 bohr; offline precision diagnosis only',
        'analysis_mode': 'Read-only saved-point arithmetic and process-ledger reconciliation',
        'new_quantum_calls_by_this_analyzer': False, 'model_API_calls_by_this_analyzer': False,
        'controller': {key: controller.get(key) for key in ('status', 'stop_reason', 'center_gradient_gate', 'displacement_admission', 'returncode', 'controller_intended_returncode')},
        'native_launch': native_launch,
        'old_A': old_columns, 'old_v3': original_columns, 'new_tight': new_columns,
        'comparison': comparison, 'scientific_qualification': qualifications, 'resources': resources,
        'read_issues': reader.issues, 'sources_changed': changed,
        'source_fingerprints': list(reader.pins.values()),
        'code_fingerprints': [item for name, item in reader.pins.items() if name.endswith('.py')],
        'scientific_boundary': 'No mixed/new full Hessian, full curvature/minimum qualification, spectrum, saddle, IRC, barrier, or mechanism; unknown is not zero'}
    summary = dict(common, points=list(rows.values()), contract=contract,
        controller_full=controller, budget_snapshot=budget)
    public_keys = ('point_id', 'stage', 'execution_state', 'returncode', 'timed_out', 'external_stop',
        'worker_status', 'failure', 'SCF_converged', 'electronic_complete', 'gradient_complete_flag',
        'raw_complete', 'qualified_point', 'energy_Eh', 'actual_final_orbital_norm',
        'strict_final_orbital_norm_passed', 'final_SCF_residuals', 'identity_checks',
        'maximum_coordinate_difference_from_planned_bohr', 'gradient_atom_norm_max_Eh_bohr',
        'gradient_atom_norm_rms_Eh_bohr', 'gradient_cartesian_component_max_Eh_bohr',
        'gradient_cartesian_component_rms_Eh_bohr', 'center_raw_gradient_gate_passed', 'read_issue')
    public = dict(common, points=[{key: row.get(key) for key in public_keys} for row in rows.values()],
        actual_worker_returncodes={key: row.get('returncode') for key, row in rows.items()})
    lines = ['# 同一M0 CF₃：收紧SCF后的中心梯度与两坐标诊断', '',
        '`review_required`；`release_eligible=false`。仅分析真实保存数据；CH₃既有结果保留。', '',
        f"实际终态：`{controller.get('status')}`；停止原因：`{controller.get('stop_reason')}`。", '',
        '| 点 | 实际状态 | 进程返回码 | 末次orbital范数 | 最大原子梯度 / Eh bohr⁻¹ |',
        '|---|---|---:|---:|---:|']
    for row in rows.values():
        lines.append(f"| {row['point_id']} | {row['execution_state']} | {row.get('returncode')} | {fmt(row.get('actual_final_orbital_norm'))} | {fmt(row.get('gradient_atom_norm_max_Eh_bohr'))} |")
    lines += ['', '末次实际orbital范数门槛仍为1e-9；中心梯度门槛仍为原子范数RMS≤3e-4、max≤4.5e-4 Eh/bohr。位移点不要求驻点。', '',
        '| 两列互易见证 / Eh bohr⁻² | 旧A | 本轮tight |', '|---|---:|---:|']
    for label, key in [('H₂₈,₁₆', 'H_28_16_Eh_bohr2'), ('H₁₆,₂₈', 'H_16_28_Eh_bohr2'),
                       ('互易差绝对值', 'absolute_antisymmetry_Eh_bohr2')]:
        values = [(x.get('mutual_pair') or {}).get(key) for x in (old_columns, new_columns)]
        lines.append(f'| {label} | {fmt(values[0])} | {fmt(values[1])} |')
    lines += ['', '新旧互易差有符号变化：'+fmt(comparison['change_in_signed_reciprocal_difference_Eh_bohr2'])+' Eh/bohr²。',
        'SCF精度对照判断：`'+comparison['SCF_precision_effect']+'`。', '',
        '4e-5 Eh/bohr²仅为预先声明的同输入重复性误差传播对照尺度，不是统计显著性，也不放宽原绝对门槛1e-4及完整矩阵相对Frobenius门槛0.001。'+
        '所有5点合格前不比较互易变化；少数列不能给出全矩阵残差或虚频数。FD1及对角FD2残差见JSON；FD2只作诊断。', '',
        '本轮实际记录worker：'+fmt(resources['new_recorded_worker_elapsed_seconds'])+'秒；累计已记录worker下界：'+
        fmt(resources['historical_plus_recorded_new_worker_hours_lower_bound'])+'小时。失败与超时也计入，完整历史CPU时间仍未知。', '',
        '根因尚未确定；局部精度敏感或未解析出变化均不能唯一归因。CF₃完整曲率与局部极小值资格未授予；不推进鞍点、IRC、势垒或机理解释。', '',
        '保存数据、真实返回码、身份/指纹和账本对账见[summary.json](summary.json)。公开进展摘要为上一级public-summary.v1.json。', '']
    args.output.mkdir(parents=True, exist_ok=False)
    for path, value in ((args.output / 'summary.json', summary), (args.public_output, public)):
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
    with (args.output / 'RESULTS_zh-CN.md').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write('\n'.join(lines))
    print(json.dumps({'status': controller.get('status'), 'qualified_points': len(gradients),
        'analysis_read_issues': reader.issues, 'source_changes': changed,
        'resource_issues': resources['issues'], 'public_summary': str(args.public_output)}, ensure_ascii=False))
    return 1 if reader.issues or changed or resources['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
