"""Build lightweight public A01 progress from an actual archived SCF summary.

This reads saved records only. It never starts a calculation or changes an
older report. S1 can retain null archive links; S2 links the known S1 commit.
"""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CURRENT = 'research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1'
TITLE = '全氟酮化学早期研究：六氟丙酮反应与六氟双酚A（双酚AF）制备'
REPO = 'https://github.com/CCcolab/Chen-Qingyun-AI4Science'
HISTORY = [
    ('qualification-20261112', '2026-11-12', '参照态与驻点资格审计', 'research/a01/qualification-20261112/REPORT_zh-CN.md',
     '核清12.511659／29.531754 kcal/mol是非驻点选定几何相对各自底物＋苯胺的单点电子能差，不构成合格DFT势垒；两侧停止结构不构成收敛终态。'),
    ('t1-continuation-20261112', '2026-11-12', '同层T1探针与分离参照', 'research/a01/oxazolone-model/t1-continuation-20261112/REPORT_zh-CN.md',
     '选定T1仅为非驻点能量／梯度探针；苯胺在受限模型内取得条件性局部极小数值支持，两侧底物参照继续精修。未得到DFT势垒或正式IRC。'),
    ('reference-continuation-20261112-v2', '2026-11-12', '两侧底物参照续算', 'research/a01/oxazolone-model/reference-continuation-20261112-v2/REPORT_zh-CN.md',
     'CH₃优化与独立梯度通过；CF₃最后完整第18点仍未合格，第19点SCF中断。停止来自单项2400秒SIGALRM，不是7200秒累计期限；该阶段完整曲率未运行。'),
    ('reference-curvature-20261113-v3', '2026-11-13', '两侧完整曲率', 'research/a01/oxazolone-model/reference-curvature-20261113-v3/REPORT_zh-CN.md',
     '两侧各157完整梯度和78列、72振动模齐全，诊断谱均0虚频。CH₃通过既定数值一致性检查，支持该受限模型内局部极小；CF₃最大反对称0.0014988913693417868 Eh/bohr²未通过，不能以零虚频补足资格。'),
    ('point-diagnosis-execution-20261113-v1', '2026-11-13', 'CF₃局部A／B点诊断', 'research/a01/oxazolone-model/cf3-point-diagnosis-execution-20261113-v1/REPORT_zh-CN.md',
     'A五点重复性通过，互易差0.0014988911403202325 Eh/bohr²。B中心主循环第4轮orbital范数9.689037768617906e-10，末次额外检查1.6225317681152e-9，核梯度前停止；后四点未执行，SCF精度对互易误差的影响未知。'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def save(path, data, replace=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not replace:
        raise FileExistsError('Use an explicit --replace for the S2 link edition: '+str(path))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')


def utc_value(source, name):
    value = source.get(name) or source.get(name+'_utc')
    if isinstance(value, dict):
        value = value.get('utc')
    return value


def local_time(value):
    if value is None:
        return None
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=8))).isoformat()


def fingerprint(source, name):
    mapping = source['code_fingerprints']
    value = mapping.get(name) or mapping.get(name+'_sha256')
    if value is None and name == 'worker':
        value = mapping.get('worker_scf.py')
    if isinstance(value, dict):
        value = value.get('sha256')
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Missing actual execution code fingerprint: '+name)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--science-root', type=Path, required=True)
    parser.add_argument('--archive-commit')
    parser.add_argument('--replace', action='store_true')
    args = parser.parse_args()
    science = args.science_root.resolve(strict=True)
    if args.archive_commit is not None and not re.fullmatch('[0-9a-f]{40}', args.archive_commit):
        raise ValueError('The evidence archive must be a complete S1 commit SHA')
    base = science/CURRENT
    source = read(base/'public-summary.v1.json')
    contract = read(base/'contract.v1.json')
    sr, resource = source['result'], source['resources']
    code_sha = {'worker': fingerprint(source, 'worker'), 'controller': fingerprint(source, 'controller')}
    attempts = resource['SCF_attempts']
    status = 'blocked_before_execution' if resource['SCF_started'] == 0 else ('passed' if sr['center_electronic_check_passed'] is True else 'failed')
    begin, finish = utc_value(source, 'started_at'), utc_value(source, 'finished_at')
    now = datetime.now(timezone.utc).isoformat()
    registry_path = science/'research/a01/branches.v1.json'
    registry = read(registry_path)
    branches = [{key: item[key] for key in ['branch_id', 'title', 'original_authors_in_registered_order', 'source_ids', 'scope', 'boundary']}
                for item in registry['branches']]
    public_scope = {
        'A01-AF': ('以第117491号说明书指定原料和产物质量，在明确计量约定下重建收率账本。',
                   '原98%收率基准仍待解释；不等于新合成、纯度测量或工艺／机理验证。'),
        'A01-MR': ('复核1960年133卷指定衍生物的折射率、密度与质量约定下的摩尔折射数字。',
                   '仅对应该文物性；不验证双酚AF结构、制备收率或性能。'),
        'A01-OX': ('研究1960年134卷CF₃／CH₃衍生物与苯胺的定性对照，苯为介质。',
                   '本轮只查同一CF₃底物中心电子终态，不验证双酚AF制备机制或原实验反应速率。')}
    for branch in branches:
        branch['scope'], branch['boundary'] = public_scope[branch['branch_id']]
    stages = []
    for stage_id, date, title, path, summary in HISTORY:
        original = science/path
        stages.append({'stage_id': stage_id, 'date': date, 'title': title, 'summary': summary,
            'original_report_path': path, 'original_report_sha256': sha(original),
            'original_report_size_bytes': original.stat().st_size,
            'original_report_availability': 'local_original_hash_only_unless_separately_distributed',
            'public_report_path': 'research/a01/STAGE_HISTORY_20261113_zh-CN.md',
            'scientific_review_status': 'review_required', 'release_eligible': False})
    current_label = {'passed': '同一中心电子终态残差检查通过', 'failed': '单次中心试验未达终态要求，已停止',
                     'blocked_before_execution': '执行前置核对阻塞，新增量化0'}[status]
    stages.append({'stage_id': source['task_id'], 'date': '2026-11-13', 'title': '中心电子终态残差检查',
        'summary': current_label+'。本轮核梯度调用0；中心结果不提升CF₃完整曲率或势垒资格。',
        'original_report_path': CURRENT+'/REPORT_zh-CN.md', 'original_report_sha256': sha(base/'REPORT_zh-CN.md'),
        'original_report_size_bytes': (base/'REPORT_zh-CN.md').stat().st_size,
        'original_report_availability': 'public_lightweight_report', 'public_report_path': CURRENT+'/REPORT_zh-CN.md',
        'scientific_review_status': 'review_required', 'release_eligible': False})
    history = {'schema_version': '1.0', 'edition_date': '2026-11-13', 'scientific_review_status': 'review_required',
        'release_eligible': False, 'scope': 'Public stage abstracts; original reports and bound raw data are preserved independently',
        'stages': stages}
    save(ROOT/'research/a01/stage-history.v1.json', history, args.replace)
    lines = ['# A01阶段记录：2026年11月12—13日', '',
        '全部为 `review_required`，`release_eligible=false`。本页公开阶段摘要；不回写旧报告，不将后补归档提交冒充执行时提交。原始本机报告按路径、SHA-256和字节登记；未分发的原件及原始包不生成下载URL。', '']
    for stage in stages:
        lines += ['<a id="'+stage['stage_id']+'"></a>', '## '+stage['date']+'｜'+stage['title'], '', stage['summary'], '',
            '原报告路径：`'+stage['original_report_path']+'`。SHA-256：`'+stage['original_report_sha256']+'`；'+str(stage['original_report_size_bytes'])+'字节。', '']
    lines += ['[机器可读阶段索引](stage-history.v1.json)。各阶段原作者归属及三分支边界见[现行登记](branches.v2.json)。', '']
    (ROOT/'research/a01/STAGE_HISTORY_20261113_zh-CN.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    current_registry = {'schema_version': '2.0', 'achievement_line': 'A01', 'title': TITLE, 'edition_date': '2026-11-13',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'historical_evaluation': registry['historical_evaluation'], 'compound_identity': registry['compound_identity'],
        'branches': branches, 'current_progress': 'public-progress.v1.json', 'stage_history': 'stage-history.v1.json',
        'history_policy': 'Original v1 registry, source IDs, authors, reports and raw values remain unchanged',
        'cross_branch_evidence_policy': registry['cross_branch_evidence_policy'],
        'source_reread_scope': 'AI reading of 133(5) p1113–1116 and134(6) p1367–1370; separate rereading of p1113/p1367 and one SU117491 specification scan; professional transcription signoff pending, grant front page absent',
        'novelty_status': 'not_claimed_systematic_originality_review_not_complete', 'experimental_validation': 'not_performed'}
    save(ROOT/'research/a01/branches.v2.json', current_registry, args.replace)
    evidence_specs = [('center-result', '本轮实际机器摘要', CURRENT+'/public-summary.v1.json'),
        ('center-electronic-result', '中心电子终态机器记录', CURRENT+'/public-evidence/center-result.v1.json'),
        ('center-raw-result', '实际点结果原字节', CURRENT+'/public-evidence/point/result.json'),
        ('center-scf-log', '完整SCF日志', CURRENT+'/public-evidence/pyscf.log'),
        ('center-final-diagnostics', '全精度末次电子诊断', CURRENT+'/public-evidence/final-scf-diagnostics.v1.json'),
        ('center-process', '真实外部进程返回记录', CURRENT+'/public-evidence/process-result.v1.json'),
        ('center-budget', '一次SCF与零梯度实际账本', CURRENT+'/public-evidence/budget.v1.json'),
        ('center-report', '本轮科学报告', CURRENT+'/REPORT_zh-CN.md'),
        ('center-protocol', '固定计算协议', CURRENT+'/PROTOCOL_zh-CN.md'),
        ('center-contract', '一次SCF与零梯度资源合同', CURRENT+'/contract.v1.json'),
        ('center-input', '中心坐标及初猜身份指纹', CURRENT+'/input.v1.json'),
        ('center-worker', '仅电子计算入口', CURRENT+'/worker_scf.py'),
        ('center-controller', '共享计数及外层停止控制器', CURRENT+'/controller.py'),
        ('progress-publication-contract', 'A01阶段进展公开合同', 'research/a01/public-progress-contract.v1.json'),
        ('original-reading-registry', '原始材料取得及AI核读范围登记', 'research/a01/sources.v2.json'),
        ('stage-history', '11月12—13日公开阶段摘要', 'research/a01/STAGE_HISTORY_20261113_zh-CN.md'),
        ('stage-history-json', '阶段原件指纹索引', 'research/a01/stage-history.v1.json')]
    # Current evidence is copied by the publication owner; use its actual bytes,
    # never fabricate a download URL for a locally retained binary archive.
    evidence = []
    for identifier, label, path in evidence_specs:
        actual = ROOT/path if (ROOT/path).is_file() else science/path
        evidence.append({'id': identifier, 'label': label, 'path': path, 'sha256': sha(actual),
            'size_bytes': actual.stat().st_size, 'fixed_url': REPO+'/blob/'+args.archive_commit+'/'+path if args.archive_commit else None})
    fixed_model = contract['fixed_model']
    model = {key: fixed_model[key] for key in ['xc', 'basis', 'solvent', 'epsilon', 'grid_level', 'solvent_grid_level', 'lmax', 'lebedev_order', 'charge', 'spin']}
    model['expected_electrons'] = 154
    for key in ['method', 'equilibrium_solvation', 'frozen']:
        model[key] = fixed_model[key]
    archive_manifest = base/'review-bundle-manifest.v1.json'
    archive_sha = None
    archive_filename = None
    archive_size = None
    if archive_manifest.is_file():
        manifest = read(archive_manifest)
        archive_entry = manifest.get('ZIP') or manifest.get('archive')
        archive_sha = (archive_entry.get('sha256') if isinstance(archive_entry, dict) else None) or manifest.get('zip_sha256')
    archives = sorted(base.glob('*.zip'))
    if len(archives) == 1:
        actual_archive_sha = sha(archives[0])
        if archive_sha is not None and archive_sha != actual_archive_sha:
            raise RuntimeError('Actual local archive differs from its declared manifest')
        archive_sha, archive_filename, archive_size = actual_archive_sha, archives[0].name, archives[0].stat().st_size
    required_observed = ['scf_converged', 'orbital_gradient_backend_norm', 'center_electronic_check_passed',
                         'electrons', 'AO_count', 'energy_Eh', 'delta_energy_Eh', 'density_change_norm']
    unavailable = None
    if not resource['SCF_started']:
        unavailable = 'Execution did not start; see the actual source summary and stop reason'
    elif any(sr.get(key) is None for key in required_observed):
        unavailable = sr.get('unavailable_reason') or source.get('stop_reason') or sr.get('stop_reason') or sr['status']
    value = {'schema_version': '1.0', 'publication_kind': 'a01_research_progress', 'title': TITLE,
        'scientific_review_status': 'review_required', 'release_eligible': False, 'timezone': 'Asia/Shanghai',
        'updated_at_utc': finish or source.get('created_utc') or now, 'evidence_archive_commit': args.archive_commit,
        'publication_contract': {'path': 'research/a01/public-progress-contract.v1.json',
            'sha256': sha(ROOT/'research/a01/public-progress-contract.v1.json')},
        'platform_work': {'classification': 'modern_offline_quantum_model_numerical_verification',
            'historical_experiment_reproduced': False, 'new_experiment': False,
            'model_API_called': False, 'novelty_claimed': False,
            'attribution': '原始化学成果及实验观察归陈庆云和原论文／说明书合作者；当前电子终态检查为平台新增模型工作'},
        'primary_materials': {
            'papers': [{'source_id': 'CQ-H12', 'volume': 133, 'pages': [1113, 1114, 1115, 1116], 'AI_read': True},
                       {'source_id': 'CQ-R01', 'volume': 134, 'pages': [1367, 1368, 1369, 1370], 'AI_read': True}],
            'professional_transcription_signoff': 'pending',
            'SU117491': {'specification_scan_pages_obtained': 1, 'grant_front_page_obtained': False,
                         '1959_grant_date_seen_in_obtained_scan': False},
            'public_summary': '已取得并由AI核读1960年133卷p.1113–1116及134卷p.1367–1370，两篇各4页、共8页；专业原文核校与结构转录签认仍待补。第117491号已取得一页说明书扫描，授予证书正页仍未取得，不以该扫描补写1959年授予落款。尚未完成系统查新，不声明首次。'},
        'execution': {'task_id': source['task_id'], 'run_id': source['run_id'], 'execution_commit': None,
            'code_sha256': code_sha,
            'started_at_utc': begin, 'finished_at_utc': finish, 'started_at_local': local_time(begin),
            'finished_at_local': local_time(finish), 'status': status,
            'stop_reason': source.get('stop_reason') or sr.get('stop_reason') or sr['status'],
            'model': model, 'scf_config': {'conv_tol': contract['internal_targets']['conv_tol'],
                'conv_tol_grad': contract['internal_targets']['conv_tol_grad'], 'max_cycle': 120},
            'budget_limits': contract['limits'],
            'result_source': {'path': CURRENT+'/public-summary.v1.json', 'sha256': sha(base/'public-summary.v1.json')},
            'result': {'scf_started': resource['SCF_started'] > 0, 'scf_converged': sr.get('scf_converged'),
                'orbital_norm': sr.get('orbital_gradient_backend_norm'), 'orbital_norm_limit': 1e-9,
                'terminal_electronic_check_passed': sr.get('center_electronic_check_passed'),
                'electron_count': sr.get('electrons'), 'AO_count': sr.get('AO_count'), 'energy_Eh': sr.get('energy_Eh'),
                'last_delta_energy_Eh': sr.get('delta_energy_Eh'), 'last_density_change_norm': sr.get('density_change_norm'),
                'TIGHT_GRAD_CONV_TOL': sr.get('TIGHT_GRAD_CONV_TOL'),
                'gradient_started': False, 'gradient_complete': False, 'gradient_reservations': 0,
                'unavailable_reason': unavailable},
            'resources': {'SCF_attempts': attempts, 'SCF_started': resource['SCF_started'],
                'SCF_complete': resource['SCF_complete'], 'gradient_attempts': 0,
                'worker_elapsed_seconds': resource.get('worker_elapsed_seconds'),
                'prior_worker_hours_lower_bound': contract['historical_recorded_worker_hours_lower_bound'],
                'cumulative_worker_hours_lower_bound': resource['cumulative_recorded_worker_hours_lower_bound'],
                'complete_history_CPU_hours': None}},
        'qualifications': {'CF3_full_curvature': 'not_qualified', 'CH3_full_curvature': 'conditional_numeric_support',
            'scf_precision_effect_on_antisymmetry': 'unknown', 'hessian_error_root_cause': 'unknown', 'DFT_barrier': 'not_qualified'},
        'branches': branches, 'history': [{'stage_id': s['stage_id'], 'date': s['date'], 'summary': s['summary'],
            'report_path': s['public_report_path'],
            'fixed_url': (REPO+'/blob/'+args.archive_commit+'/'+s['public_report_path']
                +('#'+s['stage_id'] if s['public_report_path'].endswith('STAGE_HISTORY_20261113_zh-CN.md') else ''))
                if args.archive_commit else None} for s in stages], 'evidence': evidence,
        'completed': [current_label+'。', '原A阶段五点能量与梯度具有重复性；局部互易不一致仍存在。'],
        'not_completed': ['本轮未计算中心核梯度及四个位移。', 'CF₃完整曲率资格仍未闭合；尚无合格DFT势垒排序。',
            'SCF精度对互易误差的影响、根因及原文反应性差异的解释仍未知。'],
        'next': [('审阅合格的中心电子记录，再为同一模型后续位移另立协议和预算。' if status == 'passed'
                  else '先审阅本轮未达标或前置阻塞，再决定新的中心试验协议；尚不具备后续位移准入。'),
            '中心核梯度、四个位移、完整曲率及反应路径均不在本任务自动启动。'],
        'raw_archive': {'availability': 'local_only', 'filename': archive_filename, 'sha256': archive_sha,
            'size_bytes': archive_size, 'download_url': None,
            'reason': 'Full local checkpoint/raw bundle is retained locally; public lightweight evidence is listed separately'}}
    save(ROOT/'research/a01/public-progress.v1.json', value, args.replace)
    print(json.dumps({'output': 'research/a01/public-progress.v1.json', 'source_summary_sha256': sha(base/'public-summary.v1.json'),
        'execution_status': status, 'archive_commit': args.archive_commit, 'new_quantum_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
