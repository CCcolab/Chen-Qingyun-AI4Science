"""CLI for evidence-bound, fully offline research workflows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from .common import DEFAULT_WORKSPACE, WorkbenchError, init_workspace
from .catalog import get_task, load_catalog, task_status
from .evidence import register_evidence
from .ai_exchange import export_request, import_proposal
from .jobs import enqueue, list_jobs, request_cancel, run_worker
from .report import create_report


def main() -> int:
    parser = argparse.ArgumentParser(description="陈庆云 AI 辅助研究工作台：离线证据、分析交付与受控运行")
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE,
                        help="项目内须使用被忽略的 scratch/；默认 scratch/workbench")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="初始化本地研究工作区")
    listing = sub.add_parser("tasks", help="列出任务、缺失证据和执行资格")
    listing.add_argument("--task")
    evidence = sub.add_parser("evidence-add", help="登记有定位的 UTF-8 原文／表格摘录；仍待核校")
    evidence.add_argument("--source", required=True)
    evidence.add_argument("--kind", required=True, choices=["metadata", "publisher_abstract", "primary_excerpt",
                                                           "archival_excerpt", "transcribed_table"])
    evidence.add_argument("--locator", required=True)
    evidence.add_argument("--file", type=Path, required=True)
    request = sub.add_parser("ai-export", help="导出离线 AI 分析任务包及响应模板")
    request.add_argument("--task", required=True)
    proposal = sub.add_parser("ai-import", help="校验并导入外部辅助分析；不能自动批准科研结论")
    proposal.add_argument("--file", type=Path, required=True)
    submit = sub.add_parser("enqueue", help="只允许已登记固定执行适配器入队")
    submit.add_argument("--task", required=True)
    submit.add_argument("--timeout", type=int, default=120)
    worker = sub.add_parser("work", help="执行一个离线 worker，不启动后台服务")
    worker.add_argument("--max-jobs", type=int, default=1)
    cancel = sub.add_parser("cancel", help="请求取消；由 worker 记录实际终止状态")
    cancel.add_argument("--job", required=True)
    sub.add_parser("jobs", help="读取运行状态与审计事件")
    sub.add_parser("report", help="生成新的只读本地研究概览")
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = {"workspace": str(init_workspace(args.workspace)), "mode": "offline"}
        elif args.command == "tasks":
            tasks = [get_task(args.task)] if args.task else load_catalog()["tasks"]
            result = [{**task, **task_status(task)} for task in tasks]
        elif args.command == "evidence-add":
            result = register_evidence(args.workspace, args.source, args.kind, args.locator, args.file)
        elif args.command == "ai-export":
            result = {"request": str(export_request(args.workspace, args.task)), "model_api_called": False}
        elif args.command == "ai-import":
            result = import_proposal(args.workspace, args.file)
        elif args.command == "enqueue":
            result = enqueue(args.workspace, args.task, timeout_seconds=args.timeout)
        elif args.command == "work":
            result = run_worker(args.workspace, max_jobs=args.max_jobs)
        elif args.command == "cancel":
            result = request_cancel(args.workspace, args.job)
        elif args.command == "jobs":
            result = list_jobs(args.workspace)
        else:
            result = {"report": str(create_report(args.workspace)), "scientific_review_status": "review_required"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (WorkbenchError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"工作台未通过资格或执行检查：{exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
