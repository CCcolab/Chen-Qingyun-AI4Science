"""Apply the specifically authorized A01 title and source-reading corrections.

Keeps existing URLs, anchors, source IDs and original inline source payloads.
The original export baseline is never modified by this script.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TITLE = '全氟酮化学早期研究：六氟丙酮反应与六氟双酚A（双酚AF）制备'


def change(text, old, new):
    count = text.count(old)
    if text.count(new) == 1 and count == (1 if old in new else 0):
        return text
    if count == 1:
        return text.replace(old, new, 1)
    raise ValueError('Expected exactly one known A01 editorial target: '+old[:90])


def main():
    topic = ROOT/'site/topics/early-fluoroketones/index.html'
    source = topic.read_bytes().decode('utf-8')
    pairs = [
        ('<title>专题｜早期含氟酮与双酚 AF</title>', '<title>专题｜'+TITLE+'</title>'),
        ('<h1>早期含氟酮与双酚 AF</h1>', '<h1>'+TITLE+'</h1>'),
        ('<p><a href="../../index.html#line-a01">所属成果线 A01</a> · <a href="../../index.html#topic-preview">专题索引</a> · <a href="../../index.html#source-index">公开资料索引</a></p>',
         '<p><a href="../../index.html#line-a01">所属成果线 A01</a> · <a href="../../index.html#topic-preview">专题索引</a> · <a href="../../index.html#source-index">公开资料索引</a> · <a href="#a01-ai-progress">AI辅助研究进展（待审）</a></p>'),
        ('研究问题：如何区分早期论文、综述与后来的技术回顾？', '研究问题：六氟丙酮反应与相关衍生物应如何分别复核？'),
        ('现阶段核定的是档案作者、题名、卷期及页码，俄文全文尚未逐页核译',
         '已取得134(6)p.1367–1370与133(5)p.1113–1116原页，由AI核读结构、实验数据与作者解释；专业逐句核校和结构转录签认仍待补，不能称为完整专业核译'),
        ('应取得俄文全文和学位论文核对实验细节，另查双酚 AF 相关同期技术、苏联专利原件与其他已有研究。专利原件、权利范围及优先权尚未核实，不由年代或机构回顾推断首次发明。',
         '两篇1960年原文已作AI核读；后续补专业核校、学位论文及第117491号授予正页。已取得的说明书扫描不能补足授予日期、全部权利范围或国际优先权，不能由机构历史评价推断首次发明。本轮现代中心电子检查与双酚AF制备机制分开登记。'),
        ('档案 Title、Creator、Volume、Language；仅书目。', '档案题录；134(6)p.1367–1370原页已AI核读，专业核校待补。'),
        ('〔<a href="../../index.html#source-cq-h12">CQ-H12</a>、<a href="../../index.html#source-cq-r01">CQ-R01</a>〕俄文正文待核。',
         '〔<a href="../../index.html#source-cq-h12">CQ-H12</a>、<a href="../../index.html#source-cq-r01">CQ-R01</a>〕已AI核读133卷p.1113–1116与134卷p.1367–1370；另行重读相关首页，专业核译与结构转录签认仍待补。'),
        ('第 117491 号证书涉及陈庆云、克鲁扬茨、甘巴里扬三人共同制备六氟双酚 A：1958 年申请、1959 年证书落款。申请优先权、登记和落款为不同字段，附录日期异写待按原件确认。证书不能单独证明世界首创或工业采用。',
         '已取得第117491号发明人证书的一页说明书扫描，署名顺序为克鲁扬茨、陈庆云、甘巴里扬；可见1958-07-19申请及604379/23编号。该页不显示1959年授予落款，授予证书正页尚未取得。说明书、申请字段和授予正页分别登记，不据此证明世界首创或工业采用。'),
    ]
    for old, new in pairs:
        source = change(source, old, new)
    topic.write_bytes(source.encode('utf-8'))
    for name, prefix in [('site/index.html', ''), ('site/achievements/index.html', '../')]:
        path = ROOT/name
        source = path.read_bytes().decode('utf-8')
        source = change(source, '<h3>六氟丙酮与双酚 AF</h3>', '<h3>'+TITLE+'</h3>')
        old = '<a href="'+prefix+'topics/early-fluoroketones/index.html#record-inventor-certificate">早期实验与证书档案 →</a>'
        source = change(source, old, old+' · <a href="'+prefix+'topics/early-fluoroketones/index.html#a01-ai-progress">AI辅助研究进展（待科学审阅） →</a>')
        nav_old = '<a href="'+prefix+'topics/early-fluoroketones/index.html">早期含氟酮与双酚 AF ↗</a>'
        nav_new = '<a href="'+prefix+'topics/early-fluoroketones/index.html">全氟酮化学早期研究 ↗</a>'
        if nav_old in source or nav_new in source:
            source = change(source, nav_old, nav_new)
        if name == 'site/index.html':
            source = change(source,
                '输入为既有 PFtB 内容版本 2026-11-03.1 和其登记来源；此处介绍的是既有整理成果。新增计算与预测尚未执行，也未在这里宣称科学新颖性。',
                '以上PFtB内容为既有资料整理（版本2026-11-03.1及其登记来源）。A01已开展现代离线模型计算，实际阶段见<a href="topics/early-fluoroketones/index.html#a01-ai-progress">A01待科学审阅的研究进展</a>。新实验未开展，平台不宣称科学新颖性。')
        path.write_bytes(source.encode('utf-8'))
    print(json.dumps({'edited': ['site/topics/early-fluoroketones/index.html', 'site/index.html', 'site/achievements/index.html'],
        'original_baseline_modified': False, 'new_quantum_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
