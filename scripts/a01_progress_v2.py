"""Saved-evidence publication of the same-M0 five-point precision diagnosis.

This module renders and checks records. It contains no electronic-structure
backend, subprocess launcher, model API or numerical differentiation worker.
"""
from __future__ import annotations

from datetime import timedelta
import html
import json
from pathlib import Path
from urllib.parse import quote

from a01_publication_contract import (COMMIT, PROGRESS_PATH, PROGRESS_V1_SHA256,
    PROGRESS_V2_PATH, SHA, TOPIC_PATH, digest, effective_website_entries,
    project_file, read_json)

BASE = 'research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1'
SOURCE = BASE+'/public-summary.v1.json'
CONTRACT = 'research/a01/public-progress-contract.v2.json'
TASK = 'A01-M0-CF3-TIGHT-GRAD-20261113-v1'
IDS = ['center', 'C6-y-plus', 'C6-y-minus', 'C10-y-plus', 'C10-y-minus']
SNAPSHOT_KEYS = ['points', 'old_A', 'old_v3', 'new_tight', 'comparison',
    'scientific_qualification', 'controller', 'read_issues', 'sources_changed',
    'source_fingerprints', 'actual_worker_returncodes']
EFFECTS = {
    'unknown_incomplete_or_unqualified_five_point_evidence': '五点未全部合格，SCF精度对互易误差的影响仍未知。',
    'sampled_reciprocal_difference_changes_beyond_declared_comparison_scale': '局部互易差的变化超过预先声明的重复性传播对照尺度，提示这两个采样列对本次SCF精度设置敏感；尚不能确定唯一根因。',
    'no_resolved_change_at_declared_comparison_scale_does_not_exclude_SCF_effects': '按预先声明的重复性传播对照尺度，本次未解析出局部互易差变化；这不能排除其他SCF误差或数值因素。',
}


def esc(value):
    return html.escape(str(value), quote=True)


def number(value, digits=12):
    return '未取得' if value is None else format(value, f'.{digits}g')


def render_diagnosis_block(data, data_sha256):
    """Render actual saved values; unknowns remain visibly unavailable."""
    from render_a01_progress import BEGIN, END
    execution, diagnosis = data['execution'], data['diagnosis']
    comparison, resources = diagnosis['comparison'], execution['resources']
    qualified = sum(point.get('qualified_point') is True for point in diagnosis['points'])
    rows = []
    labels = {'center': '中心', 'C6-y-plus': 'C6-y +h', 'C6-y-minus': 'C6-y −h',
              'C10-y-plus': 'C10-y +h', 'C10-y-minus': 'C10-y −h'}
    for point in diagnosis['points']:
        status = '合格诊断点' if point['qualified_point'] else ('未执行' if point['execution_state'] == 'NOT_EXECUTED' else '未合格／未完整')
        rows.append('<tr><th scope="row">'+esc(labels[point['point_id']])+'</th><td>'+esc(status)
            +'</td><td>'+esc(number(point.get('actual_final_orbital_norm')))
            +'</td><td>'+esc(number(point.get('gradient_atom_norm_max_Eh_bohr')))
            +'</td><td>'+esc(point.get('returncode') if point.get('returncode') is not None else '未取得')+'</td></tr>')
    pair_rows = []
    for label, key in [('H₂₈,₁₆', 'H_28_16_Eh_bohr2'), ('H₁₆,₂₈', 'H_16_28_Eh_bohr2'),
                       ('互易差绝对值', 'absolute_antisymmetry_Eh_bohr2')]:
        values = [(diagnosis[stage].get('mutual_pair') or {}).get(key) for stage in ['old_A', 'new_tight']]
        pair_rows.append('<tr><th scope="row">'+label+'</th><td>'+esc(number(values[0]))
                         +'</td><td>'+esc(number(values[1]))+'</td></tr>')
    center = next(point for point in diagnosis['points'] if point['point_id'] == 'center')
    fd_states, fd_rows = [], []
    for column, label in [('16', 'C6-y'), ('28', 'C10-y')]:
        record = diagnosis['new_tight']['columns'][column]
        statuses = []
        for field, name, unit in [('energy_FD_first', 'FD1', 'Eh/bohr'),
                                  ('energy_FD_second_diagonal', 'FD2', 'Eh/bohr²')]:
            values = record.get(field)
            state = '未取得' if values is None else ('通过' if values.get('passed') is True else '未通过')
            statuses.append(name+state)
            residual_key = 'absolute_residual_Eh_bohr' if name == 'FD1' else 'absolute_residual_Eh_bohr2'
            tolerance_key = 'tolerance_Eh_bohr' if name == 'FD1' else 'tolerance_Eh_bohr2'
            fd_rows.append('<tr><th scope="row">'+label+' '+name+'</th><td>'+esc(state)+'</td><td>'
                +esc(number((values or {}).get(residual_key)))+'</td><td>'
                +esc(number((values or {}).get(tolerance_key)))+'</td><td>'+unit+'</td></tr>')
        fd_states.append(label+'：'+'、'.join(statuses))
    pair = diagnosis['new_tight'].get('mutual_pair')
    if not comparison['reciprocal_comparison_eligible']:
        pair_label = '五点资格尚未闭合，已取得的局部数值只作登记，不进行SCF精度影响比较。'
    elif pair is None:
        pair_label = '本轮尚无可用的完整局部互易对照。'
    elif pair['within_original_threshold_for_this_pair_only']:
        pair_label = '这一互易对落在原绝对门槛内；仅此对局部数值，不能授予完整曲率资格。'
    else:
        pair_label = '这一互易对仍超出原绝对门槛；完整曲率资格仍未闭合。'
    columns = ''.join('<section><h3>'+title+'</h3><ul>'
        +''.join('<li>'+esc(value)+'</li>' for value in data[key])+'</ul></section>'
        for title, key in [('已完成', 'completed'), ('尚未完成', 'not_completed'), ('下一项', 'next')])
    branches = ''.join('<section class="a01-branch"><h3>'+esc(branch['title'])+'</h3><p>'+esc(branch['scope'])
        +'</p><p class="a01-small">原作者（登记顺序）：'+esc('、'.join(branch['original_authors_in_registered_order']))
        +'。'+esc(branch['boundary'])+'</p></section>' for branch in data['branches'])
    evidence = ''.join('<li>'+(('<a href="'+esc(item['fixed_url'])+'">'+esc(item['label'])+'</a>')
        if item.get('fixed_url') else esc(item['label'])+'（固定提交待归档）')
        +'<span class="a01-sha">SHA-256 '+esc(item['sha256'])+'</span></li>' for item in data['evidence'])
    history = ''.join('<li><strong>'+(('<a href="'+esc(stage['fixed_url'])+'">'+esc(stage['date'])+'</a>')
        if stage.get('fixed_url') else esc(stage['date']))+'</strong>：'+esc(stage['summary'])+'</li>'
        for stage in data['history'] if stage['stage_id'] != execution['task_id'])
    encoded = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    encoded = encoded.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    style = '''<style id="a01-progress-css">
#a01-ai-progress{scroll-margin-top:100px}#a01-ai-progress *{min-width:0}#a01-ai-progress code,#a01-ai-progress dd,#a01-ai-progress .a01-sha{overflow-wrap:anywhere;word-break:break-word}.a01-review{display:inline-block;background:#fff0d6;color:#6b4b0d;border-radius:30px;padding:.2em .8em;font-size:.82rem;font-weight:700}.a01-stage{border-left:4px solid #176e62;padding-left:16px;margin:20px 0}.a01-metrics{display:grid;grid-template-columns:minmax(140px,1fr) minmax(0,2fr);gap:6px 18px}.a01-metrics dt{font-weight:600}.a01-metrics dd{margin:0}.a01-columns,.a01-branches{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:22px 0}.a01-columns section,.a01-branch{border:1px solid #d6e0d9;border-radius:8px;padding:16px}.a01-columns h3,.a01-branch h3{margin:.1em 0 .6em}.a01-small,.a01-sha{font-size:.85rem;color:#506660}.a01-sha{display:block}.a01-boundary{background:#f6f5ef;padding:16px;border-radius:8px;font-weight:600}.a01-evidence li{margin:12px 0}.a01-table-wrap{max-width:100%;overflow-x:auto}.a01-results{border-collapse:collapse;width:100%;font-size:.88rem;margin:14px 0}.a01-results th,.a01-results td{border-bottom:1px solid #d6e0d9;text-align:left;padding:8px;vertical-align:top}.a01-results th[scope=row]{font-weight:600}.a01-unit-note{font-size:.9rem;color:#506660}@media(max-width:700px){.a01-columns,.a01-branches{grid-template-columns:1fr}.a01-metrics{grid-template-columns:1fr;gap:2px}.a01-metrics dd{margin:0 0 10px}.a01-results th,.a01-results td{padding:5px;font-size:.8rem}}
</style>'''
    archive = data.get('evidence_archive_commit')
    lines = [BEGIN, style,
        '<article id="a01-ai-progress" data-progress-source-sha256="'+esc(data_sha256)+'" data-task-id="'+esc(execution['task_id'])+'" data-run-id="'+esc(execution['run_id'])+'" data-evidence-commit="'+esc(archive or '')+'">',
        '<span class="a01-review">AI辅助研究进展 · 待科学审阅 · review_required</span>',
        '<h2>同一M0：CF₃侧SCF精度与局部互易误差</h2>',
        '<p>本平台以现代离线量化计算检验原文启发的模型问题，历史实验成果保留原作者归属。本轮仅研究噁唑酮反应性支线，不是六氟双酚A制备机制的验证。</p>',
        '<p>对象仍为M0中26原子的孤立CF₃底物参照：中性受限闭壳层，DF-RKS PBE0／def2-SVP、ddCOSMO苯（ε=2.2706）。坐标、初猜、网格及响应设置与原A一致，本轮只收紧SCF目标，诊断该底物的电子／核梯度数值一致性。</p>',
        '<div class="a01-stage"><h3>实际取得 '+str(qualified)+'／5 个合格诊断点</h3><p>执行终态：<code>'+esc(execution['status'])+'</code>。停止原因：'+esc(execution['stop_reason'])+'。完成时间：<time>'+esc(execution.get('finished_at_local') or '未取得；见执行记录')+'</time>（Asia/Shanghai）。</p></div>',
        '<p>'+esc(EFFECTS[comparison['SCF_precision_effect']])+'</p>',
        '<div class="a01-table-wrap"><table class="a01-results"><caption>本轮五点实际结果；原子梯度最大范数单位为Eh/bohr</caption><thead><tr><th scope="col">点</th><th scope="col">状态</th><th scope="col">末次orbital范数</th><th scope="col">最大原子梯度</th><th scope="col">返回码</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>',
        '<p class="a01-unit-note">最终电子orbital范数要求仍为 ≤1e-9；内部SCF能量／orbital目标为1e-12 Eh／1e-10，最多120周期。中心原子梯度RMS：'+esc(number(center.get('gradient_atom_norm_rms_Eh_bohr')))+' Eh/bohr；中心门槛RMS≤3e-4、max≤4.5e-4 Eh/bohr。位移点不要求成为驻点。</p>',
        '<div class="a01-table-wrap"><table class="a01-results"><caption>模型内部C6-y（零基坐标16）／C10-y（零基坐标28）的局部互易对照，Eh/bohr²；h=0.0005 bohr</caption><thead><tr><th scope="col">数值</th><th scope="col">旧A重复计算</th><th scope="col">本轮tight SCF</th></tr></thead><tbody>'+''.join(pair_rows)+'</tbody></table></div>',
        '<p>'+esc(pair_label)+' 新旧有符号互易差的变化：'+esc(number(comparison['change_in_signed_reciprocal_difference_Eh_bohr2']))+' Eh/bohr²。</p>',
        '<p class="a01-unit-note">原绝对反对称门槛1e-4 Eh/bohr²、完整矩阵相对Frobenius门槛0.001均保留。4e-5 Eh/bohr²只作预先声明的重复性传播对照尺度，不是统计显著性或新的合格门槛。电子orbital残差、核梯度及曲率具有不同定义，不能互换。表内数值仅作显示舍入，完整精度见固定JSON证据。</p>',
        '<p>能量与梯度的有限差分对照：'+esc('；'.join(fd_states))+'。FD2仅作对角二阶数值诊断，不作为本轮点级准入门槛；未通过项仍须保留，不能用五点完成覆盖。</p>',
        '<details><summary>展开有限差分残差与容差</summary><div class="a01-table-wrap"><table class="a01-results"><thead><tr><th scope="col">坐标／诊断</th><th scope="col">结果</th><th scope="col">绝对残差</th><th scope="col">原容差</th><th scope="col">单位</th></tr></thead><tbody>'+''.join(fd_rows)+'</tbody></table></div></details>',
        '<p class="a01-boundary">五点／两列局部诊断 ≠ 完整Hessian合格 ≠ 局部极小值认证 ≠ 势垒或机理验证。本轮没有新的完整频率或虚频数；CF₃完整曲率未合格，根因未确定。CH₃既有条件性结果保留。release_eligible=false。</p>',
        '<details><summary>本轮资源与执行身份</summary><dl class="a01-metrics">',
        '<dt>任务／运行</dt><dd><code>'+esc(execution['task_id'])+'</code><br><code>'+esc(execution['run_id'])+'</code></dd>',
        '<dt>实际SCF预约／核梯度预约</dt><dd>'+esc(resources['scalar_counters']['SCF_attempts'])+'／'+esc(resources['scalar_counters']['gradient_reservations'])+'</dd>',
        '<dt>本轮worker经过时间</dt><dd>'+esc(number(resources['new_recorded_worker_elapsed_seconds']))+'秒</dd>',
        '<dt>累计已记录worker下界</dt><dd>至少'+esc(number(resources['historical_plus_recorded_new_worker_hours_lower_bound']))+'小时；完整历史和CPU时间未知</dd>',
        '</dl><p class="a01-small">失败或超时也计入实际消耗；计划额度不计作消耗。后补归档提交不冒充执行时提交，运行代码以实际SHA-256绑定。</p></details>',
        '<div class="a01-columns">'+columns+'</div>',
        '<h3>三条独立研究分支</h3><div class="a01-branches">'+branches+'</div>',
        '<details><summary>前序结果与解释范围</summary><ol>'+history+'</ol><p>旧12.511659／29.531754 kcal/mol仍是选定非驻点几何相对各自分离反应物的单点电子能差，不构成合格DFT势垒。本轮不更新它们，也不将原文时长和分离收率换算为速率常数。</p></details>',
        '<h3>原始材料核读范围</h3><p>'+esc(data['primary_materials']['public_summary'])+'</p>',
        '<details class="a01-evidence-details"><summary>展开固定提交证据（'+str(len(data['evidence']))+'项）</summary><ul class="a01-evidence">'+evidence+'</ul></details>',
        '<p class="a01-small">新阶段证据归档提交：<code>'+esc(archive or '待建立')+'</code>。完整本机原始二进制资料未提供公开下载地址；原v1公开记录及其原固定提交保持不变。</p>',
        '</article>', '<script type="application/json" id="a01-public-progress">'+encoded+'</script>', END]
    return '\n'.join(lines)


def inspect_diagnosis_progress(root: Path, *, require_page=True, allow_unlinked=False):
    from check_a01_progress import (GITHUB_BLOB, MODEL, TITLE, finite,
        inspect_progress, timestamp)
    report = {'status': 'failed', 'scope': 'A01 five-point saved diagnosis and current static page consistency',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'DFT_started_by_check': False, 'distributed_tests_run': 0,
        'errors': [], 'evidence_checks': [], 'source_field_checks': []}
    errors = report['errors']

    def need(condition, message):
        if not condition:
            errors.append(message)

    try:
        path = project_file(root, PROGRESS_V2_PATH)
        data = read_json(path)
        json.dumps(data, allow_nan=False)
        report['public_progress_sha256'] = digest(path)
        need(data.get('schema_version') == '2.0'
             and data.get('publication_kind') == 'a01_research_progress'
             and data.get('stage_kind') == 'cf3_scf_precision_reciprocity_diagnosis',
             'Unexpected five-point A01 publication schema')
        need(data.get('title') == TITLE, 'A01 historical title changed')
        need(data.get('scientific_review_status') == 'review_required' and data.get('release_eligible') is False,
             'The diagnosis must remain pending scientific review')
        need(data.get('timezone') == 'Asia/Shanghai', 'Display timezone is missing')
        timestamp(data['updated_at_utc'], timedelta(0))
        need(data.get('previous_progress') == {'path': PROGRESS_PATH, 'sha256': PROGRESS_V1_SHA256},
             'The new edition must bind the immutable previous public record')
        prior = inspect_progress(root, require_page=False, progress_path=PROGRESS_PATH)
        need(prior['status'] == 'passed', 'Historical v1 evidence is no longer consistent: '+str(prior['errors']))
        previous = read_json(project_file(root, PROGRESS_PATH))
        need(data.get('primary_materials') == previous.get('primary_materials'),
             'This numerical diagnosis cannot change the registered primary-material reading scope')
        work = data.get('platform_work', {})
        need(work.get('classification') == 'modern_offline_quantum_model_numerical_verification'
             and all(work.get(key) is False for key in ['historical_experiment_reproduced', 'new_experiment', 'model_API_called', 'novelty_claimed']),
             'The new record cannot promote experiment reproduction, online models or novelty claims')
        publication_ref = data['publication_contract']
        need(publication_ref.get('path') == CONTRACT, 'Wrong five-point publication contract')
        contract_path = project_file(root, CONTRACT)
        need(digest(contract_path) == publication_ref.get('sha256'), 'Publication contract SHA differs')
        publication = read_json(contract_path)
        need(publication.get('contract_id') == 'A01-PUBLIC-RESEARCH-PROGRESS-20261113-v2'
             and publication.get('scientific_review_status') == 'review_required'
             and publication.get('release_eligible') is False,
             'Publication contract cannot grant scientific release')
        need(publication.get('new_quantum_calls_by_publication') == 0
             and publication.get('PF1966_UV_T1_candidate_contract_modified') is False
             and publication.get('approved_scientific_result_generated') is False,
             'Publication cannot launch calculations, change PF1966 rules or grant scientific approval')
        need(publication.get('website', {}).get('Pages_member_set_expanded_by_this_contract') is False
             and publication.get('website', {}).get('old_YouMind_baseline_retained') is True,
             'Original Pages publication set and provenance must be retained')
        execution, diagnosis = data['execution'], data['diagnosis']
        need(execution.get('task_id') == TASK and bool(execution.get('run_id')),
             'Five-point execution identity is missing or differs from the authorized task')
        need(execution.get('execution_commit') is None, 'An archive commit cannot replace an unknown execution commit')
        report['scientific_stage_outcome'] = execution.get('status')
        need(isinstance(execution.get('status'), str) and execution['status'] not in {'running', 'initializing', 'prepared', 'queued'},
             'Only an actual terminal stage may be published')
        need(isinstance(execution.get('stop_reason'), str) and bool(execution['stop_reason']), 'Actual stop reason is missing')
        source_ref = execution['result_source']
        need(source_ref.get('path') == SOURCE and publication.get('actual_result_source') == SOURCE,
             'The new edition must identify the actual saved five-point summary')
        source_path = project_file(root, SOURCE)
        need(digest(source_path) == source_ref.get('sha256'), 'Actual five-point summary SHA differs')
        source = read_json(source_path)
        need(source.get('scientific_review_status') == 'review_required' and source.get('release_eligible') is False
             and source.get('execution_commit') is None, 'The actual source must remain pending and retain its execution identity')
        need(source.get('task_id') == execution['task_id'] and source.get('run_id') == execution['run_id'],
             'Public task/run differs from the actual summary')
        need(execution.get('status') == source.get('controller', {}).get('status'),
             'Public terminal status differs from the actual controller')
        need(source.get('new_quantum_calls_by_this_analyzer') is False
             and source.get('model_API_calls_by_this_analyzer') is False,
             'The saved analysis must remain a saved-data-only operation')
        for key in SNAPSHOT_KEYS:
            equal = diagnosis.get(key) == source.get(key)
            need(equal, 'Public diagnosis differs from the actual saved source: '+key)
            report['source_field_checks'].append({'public': 'diagnosis.'+key, 'source': key, 'equal': equal})
        for public_key, source_key in [('resources', 'resources'), ('code_fingerprints', 'code_fingerprints'),
                                      ('native_launch', 'native_launch')]:
            equal = execution.get(public_key) == source.get(source_key)
            need(equal, 'Public execution differs from actual source: '+source_key)
            report['source_field_checks'].append({'public': 'execution.'+public_key, 'source': source_key, 'equal': equal})
        for prefix in ['started', 'finished']:
            utc, local = execution.get(prefix+'_at_utc'), execution.get(prefix+'_at_local')
            actual = source.get(prefix+'_at_utc') or source.get(prefix+'_at') or source.get(prefix+'_utc')
            if utc is None or local is None or actual is None:
                need(utc is None and local is None and actual is None,
                     'Unknown execution time must remain null in both timezones')
            else:
                need(timestamp(utc, timedelta(0)) == timestamp(local, timedelta(hours=8)) == timestamp(actual, timedelta(0)),
                     'Public execution timestamps differ from the actual source: '+prefix)
        calculation_contract_path = project_file(root, BASE+'/contract.v1.json')
        calculation = read_json(calculation_contract_path)
        need(calculation.get('task_id') == TASK, 'Saved calculation contract identifies another task')
        need(execution.get('budget_limits') == calculation.get('limits'), 'Public resource limits differ from the calculation contract')
        need(execution.get('model') == calculation.get('fixed_model'), 'Public model differs from the fixed calculation contract')
        for key, value in MODEL.items():
            expected_key = 'electrons' if key == 'expected_electrons' else key
            need(execution['model'].get(expected_key) == value, 'The fixed same-M0 model changed: '+key)
        for key, value in {'method': 'DF-RKS', 'equilibrium_solvation': True, 'frozen': False,
            'AO_count': 319, 'grid_response': True, 'auxbasis_response': True, 'additional_D3_D4': False}.items():
            need(execution['model'].get(key) == value, 'The authorized same-M0 method/response setting changed: '+key)
        need(execution.get('scf_config') == {'conv_tol': 1e-12, 'conv_tol_grad': 1e-10, 'max_cycle': 120,
             'final_orbital_norm_max': 1e-9}, 'SCF configuration or final acceptance threshold changed')
        need(calculation.get('internal_targets') == {'conv_tol': 1e-12, 'conv_tol_grad': 1e-10}
             and calculation.get('final_orbital_norm_max') == 1e-9, 'Actual calculation contract has different SCF targets')
        parameters = source.get('parameters', {})
        need(parameters.get('conv_tol') == 1e-12 and parameters.get('conv_tol_grad') == 1e-10
             and parameters.get('max_scf_cycles') == 120 and parameters.get('actual_final_orbital_norm_max') == 1e-9
             and parameters.get('h_bohr') == .0005 and parameters.get('normal_extra_cycle') is True
             and parameters.get('SCF_energy_or_density_change_new_acceptance_gate') is False,
             'Actual saved parameters differ from the unchanged SCF and displacement settings')
        code_pins = execution.get('code_fingerprints', [])
        need({BASE+'/worker_points.py', BASE+'/controller.py', BASE+'/analyze_diagnosis.py'} <= {pin.get('path') for pin in code_pins},
             'Actual worker/controller/analyzer fingerprints are required')
        for pin in code_pins:
            code = project_file(root, pin['path'])
            need(digest(code) == pin.get('sha256') and code.stat().st_size == pin.get('size_bytes'),
                 'Actual executed/analyzed code fingerprint differs from distributed bytes: '+pin['path'])
        limits = calculation['limits']
        need(limits.get('shared_wall_seconds') == 3000 and limits.get('per_point_wall_seconds') == 480
             and limits.get('max_SCF_attempts') == 5 and limits.get('max_gradient_reservations') == 5
             and limits.get('max_workers') == 1 and limits.get('threads_per_worker') == 4
             and limits.get('memory_mb_soft_per_worker') == 4000 and limits.get('max_SCF_cycles_per_point') == 120,
             'The authorized five-point resource ceiling changed')
        points = diagnosis['points']
        need([point.get('point_id') for point in points] == IDS, 'Exactly the five authorized points in their fixed order are required')
        for point in points:
            for key in ['energy_Eh', 'actual_final_orbital_norm', 'gradient_atom_norm_max_Eh_bohr', 'gradient_atom_norm_rms_Eh_bohr']:
                need(point.get(key) is None or finite(point[key]), 'Nonfinite actual point observation: '+point['point_id']+'/'+key)
                if key != 'energy_Eh' and finite(point.get(key)):
                    need(point[key] >= 0, 'A saved norm cannot be negative: '+point['point_id']+'/'+key)
            if point.get('qualified_point') is True:
                need(point.get('returncode') == 0 and point.get('timed_out') is False and point.get('external_stop') is False
                     and point.get('raw_complete') is True and point.get('SCF_converged') is True
                     and point.get('electronic_complete') is True and point.get('gradient_complete_flag') is True,
                     'A qualified diagnostic point lacks complete successful actual execution: '+point['point_id'])
                need(finite(point.get('actual_final_orbital_norm')) and point['actual_final_orbital_norm'] <= 1e-9,
                     'A qualified diagnostic point violates the unchanged final orbital requirement: '+point['point_id'])
                need(bool(point.get('identity_checks')) and all(value is True for value in point['identity_checks'].values()),
                     'A qualified diagnostic point lacks fixed identity checks: '+point['point_id'])
                if point['point_id'] == 'center':
                    need(point.get('center_raw_gradient_gate_passed') is True
                         and point['gradient_atom_norm_max_Eh_bohr'] <= 4.5e-4
                         and point['gradient_atom_norm_rms_Eh_bohr'] <= 3e-4, 'The center raw-gradient gate was not satisfied')
        comparison = diagnosis['comparison']
        all_five = len(points) == 5 and all(point.get('qualified_point') is True for point in points)
        need(comparison.get('all_five_points_qualified') is all_five
             and comparison.get('reciprocal_comparison_eligible') is all_five,
             'Five-point comparison eligibility differs from actual point qualifications')
        need(comparison.get('SCF_precision_effect') in EFFECTS, 'Unrecognized or overextended SCF-precision claim')
        need(comparison.get('same_input_pair_difference_comparison_scale_Eh_bohr2') == 4e-5
             and comparison.get('same_input_repetition_gradient_bound_Eh_bohr') == 1e-8,
             'The declared deterministic comparison scale changed')
        need(comparison.get('root_cause') == 'not_established' and comparison.get('full_curvature_qualification') == 'not_awarded',
             'Two-column comparison cannot establish a root cause or full curvature')
        for stage in ['old_A', 'old_v3', 'new_tight']:
            columns = diagnosis[stage]
            need(columns.get('h_bohr') == .0005 and set(columns.get('columns', {})) == {'16', '28'},
                 'Sampled coordinates or step changed: '+stage)
            need(columns.get('full_relative_Frobenius_residual') is None
                 and columns.get('frequencies_computed') is False and columns.get('imaginary_frequency_count') is None,
                 'Two columns must not masquerade as complete curvature or frequency data: '+stage)
            pair = columns.get('mutual_pair')
            if pair is not None:
                left, right = pair['H_28_16_Eh_bohr2'], pair['H_16_28_Eh_bohr2']
                need(all(finite(value) for value in [left, right])
                     and abs(pair['signed_antisymmetry_Eh_bohr2']-(left-right)) <= 1e-15
                     and abs(pair['absolute_antisymmetry_Eh_bohr2']-abs(left-right)) <= 1e-15,
                     'The reported sampled reciprocal difference is inconsistent: '+stage)
                need(pair.get('original_absolute_threshold_Eh_bohr2') == 1e-4
                     and pair.get('within_original_threshold_for_this_pair_only') is (abs(left-right) <= 1e-4)
                     and pair.get('not_a_complete_Hessian_test') is True,
                     'A local pair must retain the original threshold and its limited role: '+stage)
        if all_five:
            old_pair, new_pair = diagnosis['old_A']['mutual_pair'], diagnosis['new_tight']['mutual_pair']
            need(old_pair is not None and new_pair is not None, 'Eligible comparison requires both actual local pairs')
            change = new_pair['signed_antisymmetry_Eh_bohr2']-old_pair['signed_antisymmetry_Eh_bohr2']
            need(abs(comparison['change_in_signed_reciprocal_difference_Eh_bohr2']-change) <= 1e-15,
                 'New-versus-A reciprocal arithmetic differs')
            need(abs(comparison['absolute_change_in_signed_reciprocal_difference_Eh_bohr2']-abs(change)) <= 1e-15
                 and abs(comparison['change_in_absolute_reciprocal_difference_Eh_bohr2']
                    -(new_pair['absolute_antisymmetry_Eh_bohr2']-old_pair['absolute_antisymmetry_Eh_bohr2'])) <= 1e-15,
                 'Absolute versus signed reciprocal changes are inconsistent')
            expected_effect = ('sampled_reciprocal_difference_changes_beyond_declared_comparison_scale' if abs(change) > 4e-5
                else 'no_resolved_change_at_declared_comparison_scale_does_not_exclude_SCF_effects')
            need(comparison['SCF_precision_effect'] == expected_effect, 'Precision statement differs from the declared comparison rule')
        else:
            need(comparison['SCF_precision_effect'] == 'unknown_incomplete_or_unqualified_five_point_evidence'
                 and comparison.get('change_in_signed_reciprocal_difference_Eh_bohr2') is None,
                 'Incomplete/unqualified evidence must not receive a completed precision comparison')
        qualifications = diagnosis['scientific_qualification']
        expected = {'CH3_previous_full_curvature_result': 'retained_without_new_calculation',
            'CF3_full_curvature_qualification': 'not_awarded', 'new_full_Hessian_available': False,
            'full_relative_Frobenius_residual': None, 'new_frequencies_available': False,
            'imaginary_frequency_count': None, 'CF3_local_minimum_qualified': False,
            'saddle_or_IRC_run': False, 'barrier_or_mechanism_claim': False, 'root_cause_established': False,
            'original_full_absolute_threshold_Eh_bohr2': 1e-4, 'original_full_relative_Frobenius_threshold': .001}
        need(all(qualifications.get(key) == value for key, value in expected.items()),
             'Local diagnosis cannot promote CH3 changes, full curvature, frequencies, minima, saddle, barrier or mechanism')
        need(data.get('qualifications') == {'CF3_full_curvature': 'not_qualified',
            'CH3_full_curvature': 'conditional_numeric_support',
            'scf_precision_effect_on_sampled_reciprocity': comparison['SCF_precision_effect'],
            'hessian_error_root_cause': 'unknown', 'DFT_barrier': 'not_qualified'},
             'Public scientific qualification differs from the limited actual diagnosis')
        resources = execution['resources']
        need(resources.get('qualified_diagnostic_point_count') == sum(point.get('qualified_point') is True for point in points),
             'The resource/qualification ledger differs from the actual point list')
        if all_five:
            need(not diagnosis['read_issues'] and not diagnosis['sources_changed'] and not resources.get('issues'),
                 'Completed precision comparison requires stable, readable and reconciled actual evidence')
        elapsed = resources.get('new_recorded_worker_elapsed_seconds')
        prior_hours = resources.get('historical_recorded_worker_hours_lower_bound')
        total = resources.get('historical_plus_recorded_new_worker_hours_lower_bound')
        need(finite(elapsed) and elapsed >= 0 and prior_hours == 20.55026662453337
             and finite(total) and abs(total-(prior_hours+elapsed/3600)) <= 1e-9,
             'Cumulative actual worker accounting differs from the declared historical lower bound')
        need(resources.get('complete_historical_worker_or_CPU_hours') is None, 'Unknown complete historical/CPU usage must remain null')
        for key in ['SCF_attempts', 'SCF_started', 'gradient_reservations', 'gradient_started', 'gradient_complete']:
            value = resources.get('scalar_counters', {}).get(key)
            need(value is None or isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 5,
                 'Recorded scalar counter exceeds the authorized five-point ceiling: '+key)
        archive = data.get('raw_archive', {})
        need(archive.get('availability') == 'local_only' and archive.get('download_url') is None and bool(archive.get('reason')),
             'Local raw evidence cannot acquire an invented public download URL')
        if archive.get('sha256') is not None:
            need(isinstance(archive['sha256'], str) and SHA.fullmatch(archive['sha256']) is not None,
                 'Malformed local raw archive fingerprint')
        commit = data.get('evidence_archive_commit')
        linked = isinstance(commit, str) and COMMIT.fullmatch(commit) is not None
        need(linked or allow_unlinked and commit is None, 'Published v2 progress requires its fixed S3 commit')
        seen = set()
        for item in data['evidence']:
            need(isinstance(item.get('id'), str) and item['id'] not in seen, 'Duplicate or absent evidence identity')
            seen.add(item.get('id'))
            artifact = project_file(root, item['path'])
            equal = digest(artifact) == item.get('sha256') and artifact.stat().st_size == item.get('size_bytes')
            need(equal, 'New evidence bytes differ: '+item['path'])
            need(item.get('fixed_url') == (GITHUB_BLOB+commit+'/'+quote(item['path'], safe='/') if linked else None),
                 'New evidence links must identify their exact S3 blob: '+item['path'])
            report['evidence_checks'].append({'id': item['id'], 'path': item['path'], 'equal': equal})
        need(any(item['path'] == SOURCE and item['sha256'] == source_ref['sha256'] for item in data['evidence']),
             'The actual new source summary requires a fixed evidence entry')
        need(any(item['path'] == CONTRACT and item['sha256'] == publication_ref['sha256'] for item in data['evidence']),
             'The separate publication contract requires a fixed evidence entry')
        known_sources = {item['id'] for item in read_json(root/'site/data/public-sources.json')['sources']}
        need(len(data.get('branches', [])) == 3 and {branch.get('branch_id') for branch in data['branches']} == {'A01-AF', 'A01-MR', 'A01-OX'},
             'A01 must retain its three independently attributed branches')
        for branch in data['branches']:
            need(bool(branch.get('original_authors_in_registered_order')) and bool(branch.get('boundary'))
                 and bool(branch.get('scope')) and bool(branch.get('source_ids'))
                 and set(branch['source_ids']) <= known_sources, 'Branch authorship, source IDs or scope is missing')
            old_branch = next((item for item in previous['branches'] if item['branch_id'] == branch['branch_id']), {})
            need(all(branch.get(key) == old_branch.get(key) for key in ['title', 'source_ids', 'original_authors_in_registered_order']),
                 'This numerical diagnosis cannot rewrite branch source identities or original authorship')
        for key in ['completed', 'not_completed', 'next']:
            need(isinstance(data.get(key), list) and all(isinstance(value, str) and value for value in data[key]),
                 'Public progress must separate completed, unknown and next work: '+key)
        if require_page:
            from render_a01_progress import BEGIN, END
            page = project_file(root, 'site/'+TOPIC_PATH).read_text('utf-8')
            need(page.count(BEGIN) == page.count(END) == 1, 'The topic requires one complete progress block')
            if page.count(BEGIN) == page.count(END) == 1:
                need(page[page.index(BEGIN):page.index(END)+len(END)] == render_diagnosis_block(data, digest(path)),
                     'Visible current topic and its embedded data differ from the public record')
            _, revision = effective_website_entries(root, read_json(root/'provenance/website-baseline.json'))
            need(revision.get('public_progress_path') == PROGRESS_V2_PATH, 'The current page revision does not bind this v2 data')
            report['website_revision'] = revision
        report['status'] = 'passed' if not errors else 'failed'
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        errors.append(str(exc))
    return report
