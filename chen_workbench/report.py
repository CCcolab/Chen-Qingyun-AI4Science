"""Read-only local research overview. This report is never a Pages release."""
from __future__ import annotations

import html
import json
from pathlib import Path
from uuid import uuid4

from .catalog import load_catalog, task_status
from .common import CATALOG_PATH, now, read_json, sha256, workspace_path, safe_output, write_new
from .evidence import evidence_for_task
from .jobs import list_jobs


def create_report(workspace: Path) -> Path:
    workspace = workspace_path(workspace)
    catalog = load_catalog()
    rows = []
    for task in catalog["tasks"]:
        rows.append({**task, **task_status(task),
                     "evidence_count": len(evidence_for_task(workspace, task["task_id"]))})
    jobs = list_jobs(workspace)
    snapshot = {"schema_version": "1.0", "generated_at_utc": now(), "mode": "offline",
                "model_api_called": False, "catalog_version": catalog["catalog_version"],
                "catalog_sha256": sha256(CATALOG_PATH), "tasks": rows, "jobs": jobs,
                "proposal_count": sum((path / "import-record.json").is_file()
                                      for path in (workspace / "proposals").iterdir()),
                "scientific_review_status": "review_required", "approved_record_count": 0,
                "approved_count_scope": "this offline workbench never grants scientific approval"}
    directory = safe_output(workspace / "reports" / str(uuid4()))
    write_new(directory / "snapshot.json", snapshot)
    escape = lambda value: html.escape(str(value), quote=True)
    body = []
    for task in rows:
        blockers = "；".join(task["blockers"]) or "固定数值重放可执行；科学审阅仍待完成"
        body.append(f'<tr><td>{escape(task["achievement_line"])}</td><td>{escape(task["task_id"])}</td>'
                    f'<td>{escape(task["title"])}</td><td>{escape(task["work_type"])}</td>'
                    f'<td>{escape(task["execution_status"])}</td><td>{task["evidence_count"]}</td>'
                    f'<td>{escape(blockers)}</td></tr>')
    job_text = escape(json.dumps(jobs, ensure_ascii=False, indent=2))
    raw = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>陈庆云 AI 辅助研究工作台 · 离线概览</title>
<style>body{{font-family:system-ui,sans-serif;line-height:1.7;margin:2rem auto;max-width:1200px;padding:0 1rem;color:#202c38;background:#f7f8fa}}h1{{font-size:1.8rem}}table{{border-collapse:collapse;background:white;width:100%}}th,td{{border:1px solid #ccd3dc;padding:.6rem;text-align:left;vertical-align:top}}.scroll{{overflow:auto}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:1rem}}.status{{border-left:4px solid #aa701a;padding:1rem;background:#fff8e9}}a{{color:#135b97}}</style>
<h1>陈庆云 AI 辅助研究工作台</h1>
<p>离线概览 · {escape(snapshot["generated_at_utc"])} · {escape(catalog["catalog_version"])}</p>
<div class="status">全部科研记录保持 review_required。本工作台不授予科学批准。来源登记与已取得原文分别记录；用户提供摘录尚待独立核校。AI 建议通过引用检查，也不等于事实或机理已被验证。</div>
<h2>研究链路</h2><p>成果线 → 具体任务 → 来源摘录 → AI 分析任务包 → 有源建议导入 → 获准协议与受控运行 → 完整证据 → 专业签认 → 审定数据。</p>
<p>本轮运行器白名单仅含 PF1966-UV-T1 原表数值重放。量化计算、实验验证和其他任务继续按资料与协议缺口推进。A09 使用史料／传承证据标准，不作为分子计算任务。</p>
<h2>九条成果与传承线／十二项任务</h2>
<div class="scroll"><table><thead><tr><th>成果线</th><th>任务</th><th>问题</th><th>类型</th><th>执行资格</th><th>摘录数</th><th>缺口与限制</th></tr></thead><tbody>{"".join(body)}</tbody></table></div>
<h2>受控运行</h2><p>单 worker、固定适配器和实际墙钟时限；没有操作系统级内存隔离或量化集群。保留真实退出码、stdout、stderr、事件与运行清单。</p><pre>{job_text}</pre>
<h2>AI 辅助分析</h2><p>已导入建议 {snapshot["proposal_count"]} 项。模型 API 调用：未发生。AI 分析通过外部辅助完成，平台只校验绑定、来源引用和结构；不会执行建议中的命令或修改科研资格。</p>
<p>此报告只读，尚未进入正式网站。计算使用命令行执行，结果再按原签认流程审阅。</p>
<p><a href="snapshot.json" download>下载完整概览 JSON</a></p></html>'''
    target = safe_output(directory / "index.html")
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(raw)
    return target
