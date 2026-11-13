"""Build the new A01 progress edition from actual terminal saved evidence.

S3 stores unlinked evidence. After its commit exists, S4 binds fixed S3 URLs.
This never overwrites public-progress.v1.json or launches scientific work.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from a01_publication_contract import (COMMIT, PROGRESS_PATH, PROGRESS_V1_SHA256,
    PROGRESS_V2_PATH, REVISION_V2_PATH, digest, project_file, read_json)
from a01_progress_v2 import BASE, CONTRACT, EFFECTS, SNAPSHOT_KEYS, SOURCE, TASK

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/'


def local_time(value):
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError('Actual execution time must carry an explicit UTC offset')
    return parsed.astimezone(timezone(timedelta(hours=8))).isoformat()


def evidence_rows(root, archive_commit):
    manifest_path = project_file(root, BASE+'/PUBLIC_FILES.v1.json')
    manifest = read_json(manifest_path)
    if manifest.get('scientific_review_status') != 'review_required' or manifest.get('release_eligible') is not False:
        raise ValueError('The scientific public-file manifest cannot grant scientific release')
    rows = manifest.get('files')
    if not isinstance(rows, list) or not rows:
        raise ValueError('The actual public-file manifest must enumerate its distributed files')
    paths = {}
    for row in rows:
        name = row['path']
        if not name.startswith(BASE+'/') or PurePosixPath(name).suffix.lower() in {'.chk', '.h5', '.hdf5', '.npy', '.npz', '.zip'}:
            raise ValueError('Public progress will not promote a local binary/checkpoint/raw archive: '+name)
        file_path = project_file(root, name)
        if digest(file_path) != row['sha256'] or file_path.stat().st_size != row.get('size_bytes', row.get('bytes')):
            raise ValueError('Distributed scientific evidence differs from its public-file manifest: '+name)
        if name in paths:
            raise ValueError('Duplicate scientific evidence in public manifest: '+name)
        paths[name] = file_path
    # The manifest cannot contain its own hash. Bind it independently here.
    for name in [BASE+'/PUBLIC_FILES.v1.json', CONTRACT]:
        paths[name] = project_file(root, name)
    required = {SOURCE, BASE+'/contract.v1.json', BASE+'/worker_points.py',
                BASE+'/controller.py', BASE+'/analyze_diagnosis.py'}
    if not required <= set(paths):
        raise ValueError('The manifest lacks a required actual-result, calculation or execution artifact: '+str(sorted(required-set(paths))))
    labels = {SOURCE: '本轮五点实际机器摘要', BASE+'/contract.v1.json': '固定模型与累计预算合同',
        BASE+'/PROTOCOL_zh-CN.md': '同一M0最小补算协议', BASE+'/REPORT_zh-CN.md': '本轮科学报告',
        BASE+'/worker_points.py': '五点SCF及核梯度入口', BASE+'/controller.py': '统一计数与停止控制器',
        BASE+'/analyze_diagnosis.py': '只读两列分析及账本核算',
        BASE+'/inputs.v1.json': '五点坐标与原A初猜身份',
        BASE+'/PUBLIC_FILES.v1.json': '实际公开文件与指纹清单',
        BASE+'/results-v1/summary.json': '原始分析完整机器记录',
        BASE+'/results-v1/RESULTS_zh-CN.md': '局部互易对照数值结果',
        CONTRACT: '本阶段进展公开合同'}
    result = []
    for index, (name, path) in enumerate(sorted(paths.items()), 1):
        result.append({'id': 'five-point-evidence-'+str(index).zfill(3),
            'label': labels.get(name, name.removeprefix(BASE+'/')),
            'path': name, 'sha256': digest(path), 'size_bytes': path.stat().st_size,
            'fixed_url': REPO+archive_commit+'/'+quote(name, safe='/') if archive_commit else None})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--science-root', type=Path, required=True)
    parser.add_argument('--archive-commit', help='Actual fixed S3 commit; omit only while preparing S3')
    parser.add_argument('--replace', action='store_true', help='Replace only the unsealed new v2 edition for S4 fixed links')
    args = parser.parse_args()
    if args.archive_commit is not None and not COMMIT.fullmatch(args.archive_commit):
        parser.error('--archive-commit requires a complete lowercase 40-character SHA')
    if (ROOT/REVISION_V2_PATH).exists():
        parser.error('The current v2 revision already seals its public bytes; do not regenerate it')
    output = ROOT/PROGRESS_V2_PATH
    if output.exists() and not args.replace:
        parser.error('New v2 output already exists; --replace is reserved for the S4 binding step')
    old_path = project_file(ROOT, PROGRESS_PATH)
    if digest(old_path) != PROGRESS_V1_SHA256:
        raise ValueError('Original public progress v1 bytes changed')
    previous = read_json(old_path)
    source_path = project_file(ROOT, SOURCE)
    source = read_json(source_path)
    science = args.science_root.resolve(strict=True)
    actual_source = project_file(science, SOURCE)
    if digest(actual_source) != digest(source_path):
        raise ValueError('Publication clone summary differs from the actual scientific stage')
    if source.get('task_id') != TASK or not source.get('run_id'):
        raise ValueError('The actual saved five-point task/run identity is required')
    if source.get('execution_commit') is not None:
        raise ValueError('An archive commit must not be used as the historical execution commit')
    controller = source['controller']
    if not controller.get('status') or controller['status'] in {'prepared', 'running', 'queued', 'initializing'}:
        raise ValueError('Only actual terminal evidence may produce the new public edition')
    calculation_path = project_file(ROOT, BASE+'/contract.v1.json')
    calculation = read_json(calculation_path)
    if digest(calculation_path) != digest(project_file(science, BASE+'/contract.v1.json')):
        raise ValueError('Publication and actual scientific contracts differ')
    begin = source.get('started_at_utc') or source.get('started_at') or source.get('started_utc')
    finish = source.get('finished_at_utc') or source.get('finished_at') or source.get('finished_utc')
    evidence = evidence_rows(ROOT, args.archive_commit)
    report_candidates = [BASE+'/REPORT_zh-CN.md', BASE+'/results-v1/RESULTS_zh-CN.md']
    report_path = next((path for path in report_candidates if (ROOT/path).is_file()), None)
    if report_path is None:
        raise ValueError('A real saved stage report is required')
    data = {key: copy.deepcopy(previous[key]) for key in ['title', 'primary_materials', 'platform_work', 'branches', 'history']}
    data['platform_work']['attribution'] = '原始化学成果及实验观察归陈庆云和原论文／说明书合作者；当前五点精度诊断为平台新增离线模型工作'
    for branch in data['branches']:
        if branch['branch_id'] == 'A01-OX':
            branch['boundary'] = '本轮仅诊断同一CF₃底物中心及C6-y/C10-y局部曲率数值，不认证完整曲率、鞍点或势垒，不验证双酚AF制备机制或原实验速率。'
    for item in data['history']:
        # Historical reports are preserved bytes present in S3 as well as S1.
        project_file(ROOT, item['report_path'])
        suffix = '#'+item['stage_id'] if item['report_path'].endswith('STAGE_HISTORY_20261113_zh-CN.md') else ''
        item['fixed_url'] = REPO+args.archive_commit+'/'+quote(item['report_path'], safe='/')+suffix if args.archive_commit else None
    qualified = sum(point['qualified_point'] is True for point in source['points'])
    effect = source['comparison']['SCF_precision_effect']
    if effect not in EFFECTS:
        raise ValueError('Unknown actual SCF-precision comparison statement')
    completed = ['实际取得'+str(qualified)+'／5个合格诊断点；成功、失败及未执行项均按真实记录保留。', EFFECTS[effect]]
    unresolved = ['CF₃完整曲率及局部极小值资格未闭合；本轮没有新的完整频率或虚频数。',
        '数值误差根因仍未确定；原文定性反应性差异仍未获解释。',
        '没有合格DFT势垒、双向连接或机理认证；CH₃既有条件性结果保留。']
    for column, label in [('16', 'C6-y'), ('28', 'C10-y')]:
        fd2 = source['new_tight']['columns'][column].get('energy_FD_second_diagonal')
        if fd2 is not None and fd2.get('passed') is False:
            unresolved.insert(0, label+'的对角FD2残差未达原诊断容差；保留为未解释数值不一致，FD2不作点级资格门槛。')
    next_items = ['先审阅本轮实际五点、局部互易对照及其失败／未知项；后续补算另立协议和累计预算。',
        '本轮预算结束后不自动重试或扩大计算；完整曲率资格通过前不推进鞍点、IRC或机理解释。']
    data['history'].append({'stage_id': TASK, 'date': '2026-11-13',
        'summary': '同一M0 CF₃收紧SCF五点诊断：'+str(qualified)+'／5个点合格；'+EFFECTS[effect],
        'report_path': report_path,
        'fixed_url': REPO+args.archive_commit+'/'+quote(report_path, safe='/') if args.archive_commit else None})
    raw_archive = {'availability': 'local_only', 'filename': None, 'sha256': None,
        'size_bytes': None, 'download_url': None,
        'reason': '完整原始二进制坐标／梯度、初猜和checkpoint按源指纹在本机保留；未提供公开原始包下载。轻量实际证据另列固定链接。'}
    archives = sorted((science/BASE).glob('*.zip'))
    if len(archives) == 1:
        raw_archive.update(filename=archives[0].name, sha256=digest(archives[0]), size_bytes=archives[0].stat().st_size)
    elif len(archives) > 1:
        raw_archive['reason'] += '本阶段有多份本机包，未擅自选定唯一下载归档。'
    data.update({'schema_version': '2.0', 'publication_kind': 'a01_research_progress',
        'stage_kind': 'cf3_scf_precision_reciprocity_diagnosis',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'timezone': 'Asia/Shanghai', 'updated_at_utc': finish or source['created_utc'],
        'evidence_archive_commit': args.archive_commit,
        'previous_progress': {'path': PROGRESS_PATH, 'sha256': PROGRESS_V1_SHA256},
        'publication_contract': {'path': CONTRACT, 'sha256': digest(project_file(ROOT, CONTRACT))},
        'execution': {'task_id': source['task_id'], 'run_id': source['run_id'],
            'run_id_role': source.get('run_id_role'), 'execution_commit': None,
            'started_at_utc': begin, 'finished_at_utc': finish,
            'started_at_local': local_time(begin), 'finished_at_local': local_time(finish),
            'status': controller['status'], 'stop_reason': controller.get('stop_reason') or '实际控制器未提供停止原因；见源记录',
            'code_fingerprints': source['code_fingerprints'], 'model': calculation['fixed_model'],
            'native_launch': source.get('native_launch'),
            'scf_config': {'conv_tol': 1e-12, 'conv_tol_grad': 1e-10, 'max_cycle': 120, 'final_orbital_norm_max': 1e-9},
            'budget_limits': calculation['limits'],
            'result_source': {'path': SOURCE, 'sha256': digest(source_path)},
            'resources': source['resources']},
        'diagnosis': {key: source[key] for key in SNAPSHOT_KEYS},
        'qualifications': {'CF3_full_curvature': 'not_qualified',
            'CH3_full_curvature': 'conditional_numeric_support',
            'scf_precision_effect_on_sampled_reciprocity': effect,
            'hessian_error_root_cause': 'unknown', 'DFT_barrier': 'not_qualified'},
        'completed': completed, 'not_completed': unresolved, 'next': next_items,
        'raw_archive': raw_archive, 'evidence': evidence})
    content = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n'
    if args.replace:
        old_new = read_json(output)
        if old_new.get('execution', {}).get('result_source') != data['execution']['result_source']:
            raise ValueError('S4 cannot silently replace the actual S3 scientific source')
    with output.open('w' if args.replace else 'x', encoding='utf-8', newline='\n') as stream:
        stream.write(content)
    print(json.dumps({'status': 'built_from_saved_terminal_evidence', 'output': PROGRESS_V2_PATH,
        'task_id': source['task_id'], 'run_id': source['run_id'], 'qualified_diagnostic_points': qualified,
        'evidence_files': len(evidence), 'evidence_archive_commit': args.archive_commit,
        'DFT_started': False, 'model_API_called': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
