"""Render the A01 public progress record into a static, review-labelled block.

The research JSON stays in the repository. No network or model API is used;
the existing Pages publish member set is unchanged.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = '<!-- A01_PUBLIC_PROGRESS_BEGIN -->'
END = '<!-- A01_PUBLIC_PROGRESS_END -->'


def esc(value):
    return html.escape(str(value), quote=True)


def number(value, digits=12):
    if value is None:
        return '未取得'
    return format(value, f'.{digits}g')


def render_block(data, data_sha256):
    """Return the complete marker block; checks compare these exact bytes."""
    execution = data['execution']
    result = execution['result']
    resources = execution['resources']
    labels = {
        'passed': '同一中心电子终态残差检查通过',
        'failed': '单次中心试验未达终态要求，已停止',
        'blocked_before_execution': '执行前置核对阻塞，新增量化0',
    }
    label = labels[execution['status']]
    finished = execution['finished_at_local'] or '未启动；时间见阻塞记录'
    archive = data.get('evidence_archive_commit')
    branches = ''.join(
        '<section class="a01-branch"><h3>'+esc(branch['title'])+'</h3><p>'+esc(branch['scope'])+'</p>'
        '<p class="a01-small">原作者（登记顺序）：'+esc('、'.join(branch['original_authors_in_registered_order']))
        +'。'+esc(branch['boundary'])+'</p></section>'
        for branch in data['branches'])
    columns = ''.join(
        '<section><h3>'+title+'</h3><ul>'+''.join('<li>'+esc(value)+'</li>' for value in data[key])+'</ul></section>'
        for title, key in [('已完成', 'completed'), ('尚未完成', 'not_completed'), ('下一项', 'next')])
    history = ''.join('<li><strong>'
        +('<a href="'+esc(item['fixed_url'])+'">'+esc(item['date'])+'</a>' if item.get('fixed_url') else esc(item['date']))
        +'</strong>：'+esc(item['summary'])+'</li>'
        for item in data['history'] if item['stage_id'] != execution['task_id'])
    evidence = []
    for item in data['evidence']:
        link = ('<a href="'+esc(item['fixed_url'])+'">'+esc(item['label'])+'</a>') if item.get('fixed_url') else esc(item['label'])+'（固定提交归档待完成）'
        evidence.append('<li>'+link+'<span class="a01-sha">SHA-256 '+esc(item['sha256'])+'</span></li>')
    encoded = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    encoded = encoded.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    style = '''<style id="a01-progress-css">
#a01-ai-progress{scroll-margin-top:100px}#a01-ai-progress *{min-width:0}#a01-ai-progress code,#a01-ai-progress dd,#a01-ai-progress .a01-sha{overflow-wrap:anywhere;word-break:break-word}.a01-review{display:inline-block;background:#fff0d6;color:#6b4b0d;border-radius:30px;padding:.2em .8em;font-size:.82rem;font-weight:700}.a01-stage{border-left:4px solid #176e62;padding-left:16px;margin:20px 0}.a01-metrics{display:grid;grid-template-columns:minmax(140px,1fr) minmax(0,2fr);gap:6px 18px}.a01-metrics dt{font-weight:600}.a01-metrics dd{margin:0}.a01-columns,.a01-branches{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:22px 0}.a01-columns section,.a01-branch{border:1px solid #d6e0d9;border-radius:8px;padding:16px}.a01-columns h3,.a01-branch h3{margin:.1em 0 .6em}.a01-small,.a01-sha{font-size:.85rem;color:#506660}.a01-sha{display:block}.a01-boundary{background:#f6f5ef;padding:16px;border-radius:8px;font-weight:600}.a01-evidence li{margin:12px 0}.a01-unit-note{font-size:.9rem;color:#506660}@media(max-width:700px){.a01-columns,.a01-branches{grid-template-columns:1fr}.a01-metrics{grid-template-columns:1fr;gap:2px}.a01-metrics dd{margin:0 0 10px}}
</style>'''
    lines = [BEGIN, style,
        '<article id="a01-ai-progress" data-progress-source-sha256="'+esc(data_sha256)+'" data-task-id="'+esc(execution['task_id'])+'" data-run-id="'+esc(execution['run_id'])+'" data-evidence-commit="'+esc(archive or '')+'">',
        '<span class="a01-review">AI辅助研究进展 · 待科学审阅 · review_required</span>',
        '<h2>同一M0：中心电子残差检查</h2>',
        '<p>本平台以现代离线量化计算再检验原文启发的模型问题，历史实验成果保留原作者归属。此次只更新噁唑酮反应性支线，不是六氟双酚A制备机制的验证。</p>',
        '<div class="a01-stage"><h3>'+esc(label)+'</h3><p>完成时间：<time>'+esc(finished)+'</time>（Asia/Shanghai）。对象：原26原子CF₃底物中心、同一坐标和原始中心密度初猜。</p></div>',
        '<dl class="a01-metrics">',
        '<dt>任务／运行</dt><dd><code>'+esc(execution['task_id'])+'</code><br><code>'+esc(execution['run_id'])+'</code></dd>',
        '<dt>末次电子orbital范数</dt><dd data-metric="orbital-norm">'+esc(number(result['orbital_norm']))+'；最终要求 ≤ '+esc(number(result['orbital_norm_limit']))+'</dd>',
        '<dt>本轮内部SCF目标</dt><dd>能量 '+esc(number(execution['scf_config']['conv_tol']))+' Eh；orbital '+esc(number(execution['scf_config']['conv_tol_grad']))+'；最多 '+esc(execution['scf_config']['max_cycle'])+' 周期</dd>',
        '<dt>SCF预约尝试／核梯度调用</dt><dd>'+esc(resources['SCF_attempts'])+'／'+esc(resources['gradient_attempts'])+'；实际SCF'+('已启动' if result['scf_started'] else '未启动')+'，本轮核梯度未计算</dd>',
        '<dt>本轮worker经过时间</dt><dd>'+esc(number(resources['worker_elapsed_seconds'], 10))+' 秒</dd>',
        '<dt>累计已记录worker下界</dt><dd>至少 '+esc(number(resources['cumulative_worker_hours_lower_bound'], 12))+' 小时；完整历史及CPU时间未知</dd>',
        '</dl>',
        '<p class="a01-boundary">中心电子检查通过 ≠ 完整曲率合格 ≠ 势垒验证。CF₃完整曲率仍未合格，SCF精度对互易误差的影响及根因仍未知；release_eligible=false。</p>',
        '<p class="a01-unit-note">orbital残差是电子轨道变分残差，沿用同一后端范数定义；Eh/bohr是核坐标能量导数单位，互易曲率差使用Eh/bohr²。三者不能混用。本轮没有核梯度或频率结果。</p>',
        '<div class="a01-columns">'+columns+'</div>',
        '<h3>三条独立研究分支</h3><div class="a01-branches">'+branches+'</div>',
        '<details><summary>前序结果与解释范围</summary><ol>'+history+'</ol><p>原文反应时长与分离收率不换算成速率常数。</p></details>',
        '<h3>原始材料核读范围</h3><p>'+esc(data['primary_materials']['public_summary'])+'</p>',
        '<details class="a01-evidence-details"><summary>展开固定提交证据（'+str(len(data['evidence']))+'项）</summary><ul class="a01-evidence">'+''.join(evidence)+'</ul></details>',
        '<p class="a01-small">证据归档提交：<code>'+esc(archive or '待建立')+'</code>。这是后补归档身份，执行时源码提交号仍为未知，运行代码以实际SHA-256绑定。完整本机原始包的公开下载状态见证据索引；未提供下载URL的包不能视为已经公开。</p>',
        '</article>', '<script type="application/json" id="a01-public-progress">'+encoded+'</script>', END]
    return '\n'.join(lines)


def replace_block(page, block):
    if page.count(BEGIN) != page.count(END) or page.count(BEGIN) > 1:
        raise ValueError('Expected zero or one complete A01 progress marker pair')
    if BEGIN in page:
        start, end = page.index(BEGIN), page.index(END)+len(END)
        return page[:start]+block+page[end:]
    if page.count('</main>') != 1:
        raise ValueError('The original topic must have one main element')
    return page.replace('</main>', '\n'+block+'\n</main>', 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'research/a01/public-progress.v1.json')
    parser.add_argument('--page', type=Path, default=ROOT/'site/topics/early-fluoroketones/index.html')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    content = args.data.read_bytes()
    block = render_block(json.loads(content), hashlib.sha256(content).hexdigest())
    page = args.page.read_bytes().decode('utf-8')
    generated = replace_block(page, block)
    if args.write:
        args.page.write_bytes(generated.encode('utf-8'))
    elif generated != page:
        raise SystemExit('A01 static progress block differs; run with --write after reviewing the data')
    print(json.dumps({'page': str(args.page), 'data_sha256': hashlib.sha256(content).hexdigest(),
        'static_progress_matches': True, 'wrote_page': args.write}, ensure_ascii=False))


if __name__ == '__main__':
    main()
