"""Archive terminal saved outputs and prepare a lightweight public summary.

No quantum backend, WSL, network or subprocess calls. Checkpoints stay local.
The raw packet is finalized before the late public summary/external record,
so the public summary can contain its true SHA without a digest cycle.
"""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = ROOT/'scratch/m0-cf3-center-terminal-scf-20261113-v1'
PRIOR = HERE.parent/'cf3-point-diagnosis-execution-20261113-v1'
PUBLIC = HERE/'public-evidence'
ZIP = HERE/'review-bundle.v1.zip'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')


def pin(path):
    path = path.resolve(strict=True)
    if path.is_symlink() or not path.is_relative_to(ROOT.resolve()):
        raise ValueError('Expected a regular project evidence file')
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'size_bytes':path.stat().st_size}


def fmt(value):
    return '未知' if value is None else format(value,'.17g') if isinstance(value,(float,int)) else str(value)


def main():
    targets = [PUBLIC,ZIP,HERE/'public-summary.v1.json',HERE/'research-record.v1.json',HERE/'REPORT_zh-CN.md']
    if any(path.exists() for path in targets):
        raise FileExistsError('Fresh terminal archive required; no scientific record is overwritten')
    result = read(RAW/'result.json'); worker = read(RAW/'point/result.json')
    contract = read(HERE/'contract.v1.json'); budget = read(RAW/'shared-budget.json')
    native = read(HERE/'native-exit-observation.v1.json')
    review = read(HERE/'independent-checkpoint-review.v1.json')
    if result['budget_snapshot'] != budget:
        raise RuntimeError('Terminal/shared budget differs')
    if result.get('status') not in ['center_electronic_terminal_check_passed','single_center_trial_stopped_unqualified']:
        raise RuntimeError('Expected actual terminal scientific state')
    for key in ['gradient_reservations','gradient_started','completed_gradients']:
        if budget[key] != 0:
            raise RuntimeError('Unauthorized nuclear derivative accounting')
    if budget['total_scf_attempts'] != 1 or len(budget['reservations']) != 1:
        raise RuntimeError('Exactly one reserved trial is required')
    old_summary = read(PRIOR/'results-v1/summary.json')
    baseline = old_summary['resources']['historical_plus_recorded_new_worker_hours_lower_bound']
    if baseline != contract['historical_recorded_worker_hours_lower_bound'] or baseline < 20.51079460605307:
        raise RuntimeError('Historical resource lower bound changed or rolled back')
    elapsed = result['process']['elapsed_seconds']
    cumulative = baseline+elapsed/3600
    if abs(cumulative-result['cumulative_recorded_worker_hours_lower_bound'])>1e-12:
        raise RuntimeError('Cumulative process elapsed does not reconcile')
    diag = worker.get('final_scf_diagnostics',{})
    qualified = (result['center_electronic_check_passed'] is True
        and review['all_available_checks_passed'] is True
        and native['native_controller_returncode']==0
        and native.get('independent_saved_checkpoint_review_returncode')==0)
    status = 'center_electronic_terminal_check_passed' if qualified else 'single_center_trial_stopped_unqualified'
    PUBLIC.mkdir()
    light = {'schema_version':'1.0','task_id':contract['task_id'],'scientific_review_status':'review_required',
        'release_eligible':False,'status':status,'center_electronic_check_passed':qualified,
        'scf_started':worker.get('scf_started'),'scf_converged':worker.get('scf_converged'),
        'SCF_complete':worker.get('electronic_complete'),'energy_Eh':worker.get('energy_Eh'),
        'final_scf_diagnostics':diag,'final_electron_count':worker.get('final_electron_count'),
        'AO_count':worker.get('basis_functions'),'identity_checks_passed':worker.get('identity_checks_passed'),
        'gradient_started':worker['gradient_started'],'nuclear_gradient_calls':worker['nuclear_gradient_calls'],
        'actual_worker_returncode':result['process']['returncode'],
        'source_worker_result_sha256':sha(RAW/'point/result.json'),
        'raw_data_distribution':'Complete checkpoint/seed remain local; this is the lightweight saved-result projection'}
    save(PUBLIC/'center-result.v1.json',light)
    source_map = []
    for source,name in [(RAW/'result.json','controller-result.v1.json'),
        (RAW/'process-result.json','process-result.v1.json'),
        (RAW/'shared-budget.json','budget.v1.json'),
        (RAW/'requested-spec.json','requested-spec.v1.json'),
        (RAW/'point/result.json','point/result.json'),
        (RAW/'point/checkpoint-validation.json','checkpoint-validation.v1.json'),
        (RAW/'point/input.xyz','input.xyz'),
        (RAW/'point/final-scf-diagnostics.json','final-scf-diagnostics.v1.json'),
        (RAW/'point/electronic-history.jsonl','electronic-history.v1.jsonl'),
        (RAW/'point/pyscf.log','pyscf.log')]:
        if source.is_file():
            (PUBLIC/name).parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,PUBLIC/name)
            if sha(source)!=sha(PUBLIC/name):
                raise RuntimeError('Public evidence copy differs from original')
            source_map.append({'public_path':name,'original_raw':source.relative_to(ROOT).as_posix(),
                'sha256':sha(source),'size_bytes':source.stat().st_size,'copied_without_modification':True})
    save(PUBLIC/'source-map.v1.json',{'schema_version':'1.0','scientific_review_status':'review_required',
        'release_eligible':False,'mapping':source_map,'checkpoint_and_seed_copied_to_public':False})
    prior_worker = read(ROOT/'scratch/m0-cf3-point-diagnosis-20261113-v1/points/B-center/result.json')
    comparison = {'schema_version':'1.0','scientific_review_status':'review_required','release_eligible':False,
        'old_B': {'internal_conv_tol':1e-12,'internal_conv_tol_grad':1e-9,
            'energy_Eh':prior_worker['energy_Eh'],'final_scf_diagnostics':prior_worker['final_scf_diagnostics'],
            'main_cycle4_orbital_norm':9.689037768617906e-10,'nuclear_gradient_started':False},
        'current':light,'changed_factor':'Internal orbital target only: 1e-9 to 1e-10',
        'delta_current_minus_old_B_energy_Eh':worker.get('energy_Eh')-prior_worker['energy_Eh'] if worker.get('energy_Eh') is not None else None,
        'not_inferred':'No conclusion on reciprocal nuclear-gradient error, complete Hessian, barrier, mechanism or orbital stability'}
    save(HERE/'center-comparison.v1.json',comparison)
    started = datetime.fromtimestamp(result['started_epoch'],timezone.utc)
    finished = datetime.fromtimestamp(result['finished_epoch'],timezone.utc)
    success_text = '同一中心电子终态残差检查通过' if qualified else '单次中心试验未达终态要求，已停止'
    report = f'''# 同一CF₃中心：{success_text}

**review_required；release_eligible=false。** 本轮实际执行一次原CF₃底物中心SCF，核梯度预约及调用均为0。任务号 `{contract['task_id']}`。

内部能量目标保持1e-12 Eh，内部orbital目标由1e-9收紧至1e-10；最终平台要求仍为末次实际orbital范数≤1e-9。保留正常extra-cycle，不改PySCF判停、不追加SCF或Fock评估。原26原子完整精度Bohr坐标和原中心pre-center初猜均保持；不是以上轮B终态作新种子。

| 本轮实际结果 | 数值／状态 |
|---|---|
| 中心电子检查 | {success_text} |
| 后端SCF收敛标志 | {worker.get('scf_converged')} |
| 全精度末次orbital范数 | {fmt(diag.get('orbital_gradient_backend_norm'))} |
| 最终验收门槛 | 1e-9 |
| 末次DFT总能，含核排斥及溶剂项／Eh | {fmt(worker.get('energy_Eh'))} |
| 末次能量变化／Eh | {fmt(diag.get('delta_energy_Eh'))} |
| 末次密度变化范数 | {fmt(diag.get('density_change_norm'))} |
| 电子数／AO数 | {fmt(worker.get('final_electron_count'))}／{fmt(worker.get('basis_functions'))} |
| TIGHT_GRAD_CONV_TOL | {diag.get('TIGHT_GRAD_CONV_TOL')} |
| 真实worker返回码 | {result['process']['returncode']} |
| 真实Linux控制器返回码 | {native['native_controller_returncode']} |
| 核梯度预约／调用 | 0／0 |

orbital范数是后端定义的电子轨道残差，不是核梯度Eh/bohr。末次ΔE与密度变化照实保存，不从内部配置推断末次ΔE必定≤1e-12，也不在运行后增添独立能量门槛。模型元数据保留的grid／auxbasis响应字段只是原模型信息，本轮没有计算或验证核梯度响应。实际软件身份与源码SHA在[公开摘要](public-summary.v1.json)及[证据索引](evidence-index.v1.json)登记；执行时提交号为null，后续归档／网页提交不冒充执行时提交。

原B主循环第4轮orbital范数9.689037768617906e-10，末次extra-cycle为1.6225317681152e-9，故旧B在核梯度前停止。本轮对照见[新旧中心对照](center-comparison.v1.json)。上述变化不证明随机误差、SCF为原Hessian误差根因或迭代次数不足。

## 执行与资源

实际开始UTC：{started.isoformat()}；结束UTC：{finished.isoformat()}。时区展示采用Asia/Shanghai，对应开始{started.astimezone(timezone(timedelta(hours=8))).isoformat()}。共享600秒、单点480秒、最多1次SCF、核梯度0、单worker／4线程／4000MB软内存、max_cycle120的限额没有重置或延长。

真实worker process elapsed为{fmt(elapsed)}秒，即{fmt(elapsed/3600)} worker小时；本批执行墙钟{fmt(result['wall_elapsed_seconds'])}秒。历史下界{fmt(baseline)}小时加本轮真实经过后为至少 **{fmt(cumulative)} worker小时**。这些不是CPU时间或完整历史总量，预算额度不当作已消耗。此前被中断的WSL transport权限等待未建立科学raw或预约，属于工程等待、新增量化0；本次实际过程独立计时。

实际SCF预约／启动／电子完整为{budget['total_scf_attempts']}／{budget['SCF_started']}／{budget['SCF_complete']}；核梯度预约／启动／完整均0。停止状态：`{status}`；worker错误：`{worker.get('error')}`。真实过程与预算见[进程记录](public-evidence/process-result.v1.json)、[共享账本](public-evidence/budget.v1.json)，末次全精度值及迭代历史见[电子末次诊断](public-evidence/final-scf-diagnostics.v1.json)和[SCF原始日志](public-evidence/pyscf.log)。

## 保存数据复核与科学边界

[独立保存checkpoint复核](independent-checkpoint-review.v1.json)只读HDF5核总能、0／2占据、154电子、AO维度与坐标身份及指纹，新增量化0；不把这种保存数据复核称为独立量化复算或实验验证。[入口核验](entry-verification.v1.json)覆盖静态无核梯度路径、一次预约上限及CLI拒绝；合成标量与模拟检查不冒充真实DFT或native硬超时实测。

**中心电子检查通过不等于完整曲率通过，更不等于势垒验证。** 本轮没有中心核梯度、后四个位移、Hessian或频率，因此SCF精度对原互易误差的影响仍未知，原CF₃完整曲率资格仍未通过，根因仍未知，没有合格势垒排序。CH₃封存结果、旧矩阵／日志／结论及原作者归属保留。未检验轨道稳定性；不扩展体系、不自动开始后续量化。

本地完整证据包保存在本机本研究目录的 `review-bundle.v1.zip`，公开下载URL为null；checkpoint及seed仅本机保留。公开轻量机器摘要见[公开摘要](public-summary.v1.json)，证据指纹和本地包真实SHA见[证据索引](evidence-index.v1.json)。本地完整研究记录并不表示所有原始文件已上传GitHub。
'''
    with (HERE/'REPORT_zh-CN.md').open('x',encoding='utf-8',newline='\n') as stream: stream.write(report)
    # The local packet intentionally excludes the summary/index/record generated
    # after it. This makes a true packet SHA in the late public summary acyclic.
    selected = {}
    for directory in [HERE,RAW]:
        for path in sorted(directory.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path != ZIP:
                item = pin(path); selected[item['path']]=item
    plan_path = ROOT/contract['plan_source']
    for path in [plan_path,ROOT/contract['center']['old_result'],PRIOR/'results-v1/summary.json']:
        item=pin(path);selected[item['path']]=item
    payload={'schema_version':'1.0','scientific_review_status':'review_required','release_eligible':False,
        'payload':list(selected.values()),'omitted_late_files':'public-summary, evidence-index, external archive manifest and research-record are generated after packet finalization to avoid circular hashes'}
    payload_bytes=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    contents=(HERE.relative_to(ROOT)/'packet-contents.v1.json').as_posix()
    with ZIP.open('x+b') as stream:
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for name,item in sorted(selected.items()):
                if sha(ROOT/name)!=item['sha256']:raise RuntimeError('Packet source changed')
                archive.write(ROOT/name,name)
            archive.writestr(contents,payload_bytes)
    with zipfile.ZipFile(ZIP) as archive:
        if len(archive.infolist())!=len(selected)+1:raise RuntimeError('Unexpected packet member set')
        for info in archive.infolist():
            data=archive.read(info)
            expected={'sha256':hashlib.sha256(payload_bytes).hexdigest(),'size_bytes':len(payload_bytes)} if info.filename==contents else selected[info.filename]
            if hashlib.sha256(data).hexdigest()!=expected['sha256'] or len(data)!=expected['size_bytes']:
                raise RuntimeError('Packet member differs')
    archive_metadata={'visibility':'local_only','url':None,'sha256':sha(ZIP),'size_bytes':ZIP.stat().st_size,
        'local_project_relative_path':ZIP.relative_to(ROOT).as_posix(),
        'reason':'Complete raw checkpoint/seed are local evidence; no public download has been created'}
    save(HERE/'review-bundle-manifest.v1.json',{'schema_version':'1.0','scientific_review_status':'review_required','release_eligible':False,
        'archive':archive_metadata,'ZIP_members':len(selected)+1,'every_member_SHA_and_bytes_verified':True,'payload':list(selected.values()),
        'late_file_policy':payload['omitted_late_files']})
    source_result=pin(PUBLIC/'center-result.v1.json')
    summary={'schema_version':'1.0','task_id':contract['task_id'],'run_id':contract['task_id']+':center',
        'scientific_review_status':'review_required','release_eligible':False,'execution_commit':None,
        'started_at':started.isoformat(),'finished_at':finished.isoformat(),'display_timezone':'Asia/Shanghai',
        'result':{'status':status,'center_electronic_check_passed':qualified,'scf_converged':worker.get('scf_converged'),
            'energy_Eh':worker.get('energy_Eh'),'delta_energy_Eh':diag.get('delta_energy_Eh'),
            'orbital_gradient_backend_norm':diag.get('orbital_gradient_backend_norm'),'density_change_norm':diag.get('density_change_norm'),
            'TIGHT_GRAD_CONV_TOL':diag.get('TIGHT_GRAD_CONV_TOL'),'electrons':worker.get('final_electron_count'),
            'AO_count':worker.get('basis_functions'),'gradient_started':False,'nuclear_gradient_calls':0},
        'resources':{'SCF_attempts':budget['total_scf_attempts'],'SCF_started':budget['SCF_started'],'SCF_complete':budget['SCF_complete'],
            'gradient_reservations':0,'worker_elapsed_seconds':elapsed,'worker_elapsed_hours':elapsed/3600,
            'execution_wall_seconds':result['wall_elapsed_seconds'],'historical_worker_hours_lower_bound':baseline,
            'cumulative_recorded_worker_hours_lower_bound':cumulative,'complete_historical_or_CPU_hours':None},
        'parameters':{'internal_conv_tol':1e-12,'internal_conv_tol_grad':1e-10,'max_cycle':120,'terminal_orbital_max':1e-9},
        'code_fingerprints':{'worker':sha(HERE/'worker_scf.py'),'controller':sha(HERE/'controller.py'),'contract':sha(HERE/'contract.v1.json')},
        'actual_software':worker.get('software'),'software_source_fingerprints':worker.get('software_source_fingerprints'),
        'actual_worker_returncode':result['process']['returncode'],'actual_controller_returncode':native['native_controller_returncode'],
        'result_source':source_result,'raw_archive':archive_metadata,
        'full_curvature_qualified':False,'SCF_effect_on_reciprocal_error':'unknown','cause':'unknown','barrier_ranking_qualified':False,
        'new_full_curvature_result':None,'new_full_curvature_null_reason':'Not computed in this center-electronic-only protocol',
        'remaining_work':['Four displaced points under a new protocol','Complete qualified curvature','Target saddle and path validation only after reference qualification'],
        'published_authorship':'Historical findings remain attributed to their original authors; this is a modern platform numerical diagnostic',
        'nuclear_gradient_response_metadata':'Grid/auxbasis fields inherit model intent; no nuclear gradient was calculated or tested in this trial'}
    save(HERE/'public-summary.v1.json',summary)
    evidence=[]
    for path in [HERE/'PROTOCOL_zh-CN.md',HERE/'contract.v1.json',HERE/'input.v1.json',HERE/'worker_scf.py',HERE/'controller.py',
        HERE/'REPORT_zh-CN.md',HERE/'public-summary.v1.json',HERE/'independent-checkpoint-review.v1.json',*[p for p in sorted(PUBLIC.rglob('*')) if p.is_file()]]:
        evidence.append(pin(path))
    save(HERE/'evidence-index.v1.json',{'schema_version':'1.0','scientific_review_status':'review_required','release_eligible':False,
        'task_id':contract['task_id'],'lightweight_publication_candidates':evidence,'raw_archive':archive_metadata,
        'publication_state':'Prepared locally; GitHub/Pages actual publication is recorded separately by the publication task'})
    artifacts={}
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            item=pin(path);artifacts[item['path']]={k:item[k] for k in ['sha256','size_bytes']}
    raw_files=[pin(path) for path in sorted(RAW.rglob('*')) if path.is_file()]
    save(HERE/'research-record.v1.json',{'schema_version':'1.0','task_id':contract['task_id'],
        'scientific_review_status':'review_required','release_eligible':False,'execution_commit':None,
        'status':status,'artifacts':artifacts,'raw_files':raw_files,'raw_archive':archive_metadata,
        'resources':summary['resources'],'scientific_boundary':'Center electronic result only; no nuclear gradients, displaced points, full curvature or barrier validation',
        'source_integrity_after':result['source_integrity_after'],'independent_saved_checkpoint_review':review['all_available_checks_passed'],
        'new_quantum_calls_by_archival':0,'original_working_tree_or_old_scientific_records_modified':False,
        'archive_order':'Packet finalized first; external summary/index/manifest/record bind packet SHA without circular digest'})
    print(json.dumps({'status':status,'terminal_orbital_norm':diag.get('orbital_gradient_backend_norm'),
        'worker_elapsed_seconds':elapsed,'cumulative_lower_bound':cumulative,
        'public_summary':str(HERE/'public-summary.v1.json'),'ZIP_sha256':sha(ZIP),'ZIP_bytes':ZIP.stat().st_size},ensure_ascii=False))


if __name__=='__main__':
    main()
