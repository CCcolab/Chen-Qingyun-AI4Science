"""Validate A01 public progress against saved evidence and static HTML.

No SCF, DFT, model API or unit-test invocation. A correctly recorded failed or
blocked scientific stage can pass this publication-consistency check.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import re
from urllib.parse import quote

from a01_publication_contract import (COMMIT, PROGRESS_PATH, REVISION_PATH, SHA,
    PROGRESS_V2_PATH, TOPIC_PATH, current_progress_path, digest,
    effective_website_entries, project_file, read_json)

ROOT = Path(__file__).resolve().parents[1]
TITLE = '全氟酮化学早期研究：六氟丙酮反应与六氟双酚A（双酚AF）制备'
QUALIFICATIONS = {'CF3_full_curvature': 'not_qualified',
    'CH3_full_curvature': 'conditional_numeric_support',
    'scf_precision_effect_on_antisymmetry': 'unknown',
    'hessian_error_root_cause': 'unknown', 'DFT_barrier': 'not_qualified'}
MODEL = {'xc': 'PBE0', 'basis': 'def2-svp', 'solvent': 'ddCOSMO', 'epsilon': 2.2706,
    'grid_level': 2, 'solvent_grid_level': 1, 'lmax': 6, 'lebedev_order': 17,
    'charge': 0, 'spin': 0, 'expected_electrons': 154}
SCF = {'conv_tol': 1e-12, 'conv_tol_grad': 1e-10, 'max_cycle': 120}
GITHUB_BLOB = 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/'


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def timestamp(value, offset):
    if not isinstance(value, str):
        raise ValueError('Expected an explicit timestamp')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() != offset:
        raise ValueError('Timestamp has an unexpected or absent timezone: '+value)
    return parsed


def inspect_progress(root: Path = ROOT, *, require_page=True, allow_unlinked=False,
                     progress_path=None) -> dict:
    selected = progress_path or current_progress_path(root)
    if selected == PROGRESS_V2_PATH:
        from a01_progress_v2 import inspect_diagnosis_progress
        return inspect_diagnosis_progress(root, require_page=require_page,
            allow_unlinked=allow_unlinked)
    if selected != PROGRESS_PATH:
        raise ValueError('Unsupported explicit A01 progress data path')
    report = {'status': 'failed', 'scope': 'A01 saved evidence, public JSON and static page consistency',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'DFT_started_by_check': False, 'distributed_tests_run': 0,
        'errors': [], 'evidence_checks': [], 'source_field_checks': []}
    errors = report['errors']

    def need(condition, message):
        if not condition:
            errors.append(message)

    try:
        path = project_file(root, PROGRESS_PATH); data = read_json(path)
        json.dumps(data, allow_nan=False)
        report['public_progress_sha256'] = digest(path)
        need(data.get('schema_version') == '1.0', 'Unexpected A01 progress schema')
        need(data.get('publication_kind') == 'a01_research_progress', 'This interface is A01 progress, not PF1966 reviewed-result export')
        need(data.get('title') == TITLE, 'A01 topic title differs from the registered historical branch title')
        need(data.get('scientific_review_status') == 'review_required' and data.get('release_eligible') is False,
             'Public progress must retain pending scientific review and release_eligible=false')
        need(data.get('timezone') == 'Asia/Shanghai', 'A01 display timezone must be explicit')
        timestamp(data.get('updated_at_utc'), timedelta(0))
        publication_ref = data['publication_contract']
        need(publication_ref.get('path') == 'research/a01/public-progress-contract.v1.json',
             'Public A01 progress must identify its separate progress-publication contract')
        publication_path = project_file(root, publication_ref['path'])
        need(digest(publication_path) == publication_ref.get('sha256'), 'Progress-publication contract fingerprint differs')
        publication = read_json(publication_path)
        need(publication.get('contract_id') == 'A01-PUBLIC-RESEARCH-PROGRESS-20261113-v1'
             and publication.get('publication_kind') == 'a01_research_progress'
             and publication.get('scientific_review_status') == 'review_required'
             and publication.get('release_eligible') is False,
             'The separate A01 publication contract cannot promote scientific release')
        need(publication.get('PF1966_UV_T1_candidate_contract_modified') is False
             and publication.get('approved_scientific_result_generated') is False
             and publication.get('new_quantum_calls_by_publication') == 0,
             'A01 public progress must not modify PF1966 release rules, grant approval or launch quantum work')
        need(publication.get('website', {}).get('Pages_member_set_expanded_by_this_contract') is False
             and publication.get('website', {}).get('old_YouMind_baseline_retained') is True,
             'The A01 progress contract must retain the original website provenance and member set')
        execution = data['execution']; outcome = execution.get('status')
        need(outcome in {'passed', 'failed', 'blocked_before_execution'}, 'Unknown actual center-stage outcome')
        report['scientific_stage_outcome'] = outcome
        need(execution.get('execution_commit') is None, 'A later archive commit must not be used as the historical execution commit')
        need(execution.get('task_id') == 'A01-M0-CF3-CENTER-TERMINAL-SCF-20261113-v1', 'Progress must identify the single authorized center task')
        need(isinstance(execution.get('run_id'), str) and bool(execution['run_id']), 'Run identity is missing')
        for key, expected in MODEL.items():
            need(execution.get('model', {}).get(key) == expected, 'Unexpected fixed M0 model field: '+key)
        for key, expected in SCF.items():
            need(execution.get('scf_config', {}).get(key) == expected, 'Unexpected center SCF configuration: '+key)
        result, resources = execution['result'], execution['resources']
        need(result.get('orbital_norm_limit') == 1e-9, 'The final orbital threshold must not be relaxed')
        for key in ['gradient_started', 'gradient_complete']:
            need(result.get(key) is False, 'This task does not authorize a nuclear gradient: '+key)
        need(result.get('gradient_reservations') == 0 and resources.get('gradient_attempts') == 0,
             'Nuclear-gradient reservations and calls must both be zero')
        need(resources.get('SCF_attempts') in (0, 1) and not isinstance(resources.get('SCF_attempts'), bool),
             'The center task permits at most one charged SCF attempt')
        for key in ['orbital_norm', 'energy_Eh', 'last_delta_energy_Eh', 'last_density_change_norm']:
            value = result.get(key)
            need(value is None or finite(value), 'Nonfinite or nonnumeric saved result: '+key)
        if any(result.get(key) is None for key in ['orbital_norm', 'energy_Eh', 'electron_count', 'AO_count']):
            need(isinstance(result.get('unavailable_reason'), str) and bool(result['unavailable_reason'].strip()),
                 'Missing observations need an explicit reason; unknown must not be replaced with zero')
        if outcome == 'passed':
            need(result.get('scf_started') is True and result.get('scf_converged') is True,
                 'A passed center stage requires a real converged SCF')
            need(result.get('terminal_electronic_check_passed') is True,
                 'A passed center stage requires the recorded terminal electronic check')
            need(finite(result.get('orbital_norm')) and result['orbital_norm'] <= 1e-9,
                 'A passed center stage exceeds the unchanged final orbital threshold')
            need(result.get('electron_count') == 154, 'The registered neutral restricted center has 154 electrons')
            need(isinstance(result.get('AO_count'), int) and result['AO_count'] >= 77, 'Actual AO count is missing')
            need(resources.get('SCF_attempts') == 1, 'A passed center stage requires exactly one SCF attempt')
            need(all(finite(result.get(key)) for key in ['energy_Eh', 'last_delta_energy_Eh', 'last_density_change_norm']),
                 'A passed center stage needs finite recorded energy and terminal diagnostics')
        elif outcome == 'failed':
            need(result.get('terminal_electronic_check_passed') is False, 'A failed stage cannot claim terminal acceptance')
        else:
            need(result.get('scf_started') is False, 'A blocked-before-execution stage cannot claim SCF startup')
            need(result.get('terminal_electronic_check_passed') in (None, False), 'A blocked stage cannot claim terminal acceptance')
        need(isinstance(execution.get('stop_reason'), str) and bool(execution['stop_reason']), 'Actual stop reason is missing')
        need(resources.get('complete_history_CPU_hours') is None, 'Unknown historical CPU time must remain null')
        elapsed = resources.get('worker_elapsed_seconds')
        prior, cumulative = resources.get('prior_worker_hours_lower_bound'), resources.get('cumulative_worker_hours_lower_bound')
        need(finite(elapsed) and elapsed >= 0, 'Actual center process elapsed is absent or invalid')
        if outcome == 'passed':
            need(finite(elapsed) and elapsed <= 480, 'A passed center stage exceeds its single-point wall limit')
        need(finite(prior) and prior >= 20.51079460605307-1e-10, 'The recorded historical lower bound regressed')
        need(finite(cumulative) and finite(prior) and finite(elapsed)
             and abs(cumulative-(prior+elapsed/3600)) <= 1e-9, 'Cumulative worker arithmetic differs from actual process elapsed')
        for key, expected in QUALIFICATIONS.items():
            need(data.get('qualifications', {}).get(key) == expected, 'Center acceptance must not promote scientific qualification: '+key)
        for prefix in ['started', 'finished']:
            utc, local = execution.get(prefix+'_at_utc'), execution.get(prefix+'_at_local')
            if utc is None or local is None:
                need(outcome == 'blocked_before_execution' and utc is None and local is None,
                     'Only an unstarted stage may have unknown execution timestamps')
            else:
                u, l = timestamp(utc, timedelta(0)), timestamp(local, timedelta(hours=8))
                need(u == l, 'UTC and Beijing timestamps do not identify the same instant')
        if execution.get('started_at_utc') and execution.get('finished_at_utc'):
            need(timestamp(execution['finished_at_utc'], timedelta(0)) >= timestamp(execution['started_at_utc'], timedelta(0)),
                 'Execution finish precedes start')
        commit = data.get('evidence_archive_commit')
        linked = isinstance(commit, str) and COMMIT.fullmatch(commit) is not None
        need(linked or allow_unlinked and commit is None, 'Published progress needs its fixed S1 evidence commit')
        evidence = data.get('evidence')
        need(isinstance(evidence, list) and bool(evidence), 'Evidence list is missing')
        seen = set()
        for item in evidence or []:
            need(item.get('id') not in seen and isinstance(item.get('id'), str), 'Duplicate or missing evidence identity')
            seen.add(item.get('id'))
            artifact = project_file(root, item['path'])
            equal = digest(artifact) == item.get('sha256') and artifact.stat().st_size == item.get('size_bytes')
            need(equal, 'Evidence bytes differ: '+item['path'])
            if linked:
                need(item.get('fixed_url') == GITHUB_BLOB+commit+'/'+quote(item['path'], safe='/'),
                     'Evidence link must use the fixed S1 commit: '+item['path'])
            report['evidence_checks'].append({'id': item['id'], 'path': item['path'], 'equal': equal})
        history = data.get('history', [])
        need(isinstance(history, list) and bool(history), 'A01 stage history is missing')
        seen_stages = set()
        for stage in history:
            identifier = stage.get('stage_id')
            need(isinstance(identifier, str) and identifier not in seen_stages, 'Duplicate or absent historical stage identity')
            seen_stages.add(identifier)
            historical_report = project_file(root, stage['report_path'])
            suffix = ''
            if stage['report_path'].endswith('STAGE_HISTORY_20261113_zh-CN.md'):
                suffix = '#'+str(identifier)
                need('<a id="'+str(identifier)+'"></a>' in historical_report.read_text('utf-8'),
                     'Fixed historical stage anchor is missing: '+str(identifier))
            if linked:
                need(stage.get('fixed_url') == GITHUB_BLOB+commit+'/'+quote(stage['report_path'], safe='/')+suffix,
                     'Historical stage link must identify its fixed S1 report: '+str(identifier))
        source_ref = execution['result_source']
        need(publication.get('actual_result_source') == source_ref.get('path'),
             'Publication contract and progress identify different actual center results')
        need(any(item.get('id') == 'progress-publication-contract'
                 and item.get('path') == publication_ref.get('path')
                 and item.get('sha256') == publication_ref.get('sha256') for item in evidence or []),
             'The separate A01 progress-publication contract needs its fixed evidence link')
        need(any(item.get('id') == 'center-result' and item.get('path') == source_ref.get('path')
                 and item.get('sha256') == source_ref.get('sha256') for item in evidence or []),
             'The actual center summary must have a fixed center-result evidence link')
        source_path = project_file(root, source_ref['path'])
        need(digest(source_path) == source_ref.get('sha256'), 'Actual center summary bytes differ from declared result source')
        source = read_json(source_path)
        json.dumps(source, allow_nan=False)
        need(source.get('task_id') == execution['task_id'] and source.get('run_id') == execution['run_id'],
             'Public task/run identity differs from the saved actual center summary')
        need(source.get('scientific_review_status') == 'review_required' and source.get('release_eligible') is False,
             'Saved center summary must remain pending review')
        need(source.get('execution_commit') is None, 'A later archive commit cannot replace the unknown execution commit in the actual source')
        for prefix in ['started', 'finished']:
            observed_time = source.get(prefix+'_at') or source.get(prefix+'_at_utc')
            if isinstance(observed_time, dict):
                observed_time = observed_time.get('utc')
            published_time = execution.get(prefix+'_at_utc')
            equal_time = (published_time is None and observed_time is None)
            if published_time is not None and observed_time is not None:
                equal_time = timestamp(published_time, timedelta(0)) == timestamp(observed_time, timedelta(0))
            need(equal_time, 'Published execution time differs from actual source: '+prefix)
        parameters = source.get('parameters', {})
        for public_key, source_key in [('conv_tol', 'internal_conv_tol'), ('conv_tol_grad', 'internal_conv_tol_grad'), ('max_cycle', 'max_cycle')]:
            need(execution['scf_config'].get(public_key) == parameters.get(source_key),
                 'Published SCF configuration differs from actual source: '+public_key)
        need(parameters.get('terminal_orbital_max') == 1e-9, 'Actual source has a different final orbital acceptance threshold')
        need(source.get('full_curvature_qualified') is False and source.get('barrier_ranking_qualified') is False
             and source.get('SCF_effect_on_reciprocal_error') == 'unknown' and source.get('cause') == 'unknown',
             'The actual center source must not promote curvature, barrier or causal claims')
        source_result, source_resources = source['result'], source['resources']
        mappings = {'scf_converged': 'scf_converged', 'orbital_norm': 'orbital_gradient_backend_norm',
            'terminal_electronic_check_passed': 'center_electronic_check_passed', 'electron_count': 'electrons',
            'AO_count': 'AO_count', 'energy_Eh': 'energy_Eh', 'last_delta_energy_Eh': 'delta_energy_Eh',
            'last_density_change_norm': 'density_change_norm', 'gradient_started': 'gradient_started'}
        for public_key, source_key in mappings.items():
            equal = result.get(public_key) == source_result.get(source_key)
            need(equal, 'Public result differs from actual saved center field: '+public_key)
            report['source_field_checks'].append({'public': 'execution.result.'+public_key,
                'source': 'result.'+source_key, 'equal': equal})
        need(source_result.get('nuclear_gradient_calls') == 0 and source_resources.get('gradient_reservations') == 0,
             'Saved source reveals unauthorized nuclear-gradient work')
        if outcome == 'passed':
            need(source_resources.get('SCF_complete') == 1,
                 'A passed stage needs a complete observed SCF in the actual source ledger')
            need(source.get('actual_worker_returncode') == 0 and source.get('actual_controller_returncode') == 0,
                 'A passed center stage requires successful actual worker and controller exits')
            need(finite(source_resources.get('execution_wall_seconds')) and source_resources['execution_wall_seconds'] <= 600,
                 'A passed stage exceeds its shared execution window')
        for public_key, source_key in [('SCF_attempts', 'SCF_attempts'), ('worker_elapsed_seconds', 'worker_elapsed_seconds'),
                ('cumulative_worker_hours_lower_bound', 'cumulative_recorded_worker_hours_lower_bound')]:
            need(resources.get(public_key) == source_resources.get(source_key), 'Public resources differ from saved actual source: '+public_key)
        need(source_resources.get('SCF_started') in (0, 1), 'Saved source lacks the actual SCF startup count')
        need(result.get('scf_started') == bool(source_resources.get('SCF_started')), 'SCF startup differs from the actual saved source')
        fingerprints = source.get('code_fingerprints', {})
        for key in ['worker', 'controller']:
            value = fingerprints.get(key) or fingerprints.get(key+'_sha256')
            if value is None:
                value = fingerprints.get('worker_scf.py' if key == 'worker' else 'controller.py')
            expected = value.get('sha256') if isinstance(value, dict) else value
            need(execution.get('code_sha256', {}).get(key) == expected and isinstance(expected, str) and SHA.fullmatch(expected) is not None,
                 'Execution code fingerprint differs from actual source: '+key)
        branches = data.get('branches', [])
        need(len(branches) == 3 and {b.get('branch_id') for b in branches} == {'A01-AF', 'A01-MR', 'A01-OX'},
             'A01 must retain its three separately attributed scientific branches')
        known_sources = {item['id'] for item in read_json(root/'site/data/public-sources.json')['sources']}
        for branch in branches:
            need(bool(branch.get('original_authors_in_registered_order')) and bool(branch.get('boundary'))
                 and bool(branch.get('scope')) and bool(branch.get('source_ids'))
                 and set(branch['source_ids']) <= known_sources,
                 'Branch attribution, original source identities or scope is missing')
        for key in ['completed', 'not_completed', 'next']:
            need(isinstance(data.get(key), list) and all(isinstance(text, str) and text for text in data[key]),
                 'A01 public progress must distinguish completed, unresolved and next work: '+key)
        archive = data.get('raw_archive', {})
        need(archive.get('availability') == 'local_only' and archive.get('download_url') is None
             and isinstance(archive.get('sha256'), str) and SHA.fullmatch(archive['sha256']) is not None
             and bool(archive.get('reason')), 'An unhosted raw archive must not acquire an invented public download URL')
        if require_page:
            from render_a01_progress import render_block
            page = project_file(root, 'site/'+TOPIC_PATH).read_text('utf-8')
            begin, end = '<!-- A01_PUBLIC_PROGRESS_BEGIN -->', '<!-- A01_PUBLIC_PROGRESS_END -->'
            need(page.count(begin) == page.count(end) == 1, 'A01 static progress markers must be unique')
            if page.count(begin) == page.count(end) == 1:
                block = page[page.index(begin):page.index(end)+len(end)]
                need(block == render_block(data, digest(path)), 'Visible static A01 block differs from its public JSON')
            _, revision = effective_website_entries(root, read_json(root/'provenance/website-baseline.json'))
            need(revision['present'], 'A changed A01 page requires its explicit revision contract')
            report['website_revision'] = revision
        report['status'] = 'passed' if not errors else 'failed'
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        errors.append(str(exc))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--data-only', action='store_true', help='Preparation check, without page/revision checks')
    parser.add_argument('--allow-unlinked', action='store_true', help='Permit a null archive commit only while preparing an evidence edition')
    parser.add_argument('--data', choices=[PROGRESS_PATH, PROGRESS_V2_PATH],
                        help='Explicit edition for archive preparation or historical verification')
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error('--output must be a fresh JSON evidence path')
    report = inspect_progress(require_page=not args.data_only, allow_unlinked=args.allow_unlinked,
                              progress_path=args.data)
    # S3 may contain the real new evidence before S4 changes the current page.
    # Check that saved successor too; keep the historical page as current until
    # its separately bound revision and registry are created.
    if (args.data is None and current_progress_path(ROOT) == PROGRESS_PATH
            and (ROOT/PROGRESS_V2_PATH).is_file()):
        successor = inspect_progress(require_page=False, allow_unlinked=True,
                                     progress_path=PROGRESS_V2_PATH)
        report['prepared_successor_data_check'] = successor
        if successor['status'] != 'passed':
            report['errors'].extend('Prepared v2 data: '+message for message in successor['errors'])
            report['status'] = 'failed'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps({'status': report['status'], 'scientific_stage_outcome': report.get('scientific_stage_outcome'),
        'evidence_checks': len(report['evidence_checks']), 'source_field_checks': len(report['source_field_checks']),
        'prepared_successor_status': report.get('prepared_successor_data_check', {}).get('status'),
        'DFT_started_by_check': False, 'distributed_tests_run': 0, 'errors': report['errors']}, ensure_ascii=False))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
