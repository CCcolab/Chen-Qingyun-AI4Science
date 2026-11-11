import argparse
from pathlib import Path
import json
import sys

from .uv_replay import ReproducibilityError
from .run_record import create_run, failure_error, new_run_directory, utc_now, write_failure_record


def main():
    parser = argparse.ArgumentParser(description="重放陈庆云团队 1966 年论文表 1 的数值关系")
    parser.add_argument("--data", type=Path, default=Path("data/pftb1966_table1.csv"))
    parser.add_argument("--protocol", type=Path, default=Path("protocols/pftb1966_uv.json"))
    parser.add_argument("--sources", type=Path, default=Path("data/sources.json"))
    parser.add_argument("--output", type=Path, help="新建或空运行目录；默认 scratch/runs/<UTC>-<UUID>")
    args = parser.parse_args()
    started = utc_now()
    output = args.output if args.output is not None else new_run_directory()
    try:
        manifest_path = create_run(args.data, args.protocol, args.sources,
                                   output,
                                   invocation={"kind": "cli", "argv": list(sys.argv)})
    except (ReproducibilityError, OSError, KeyError, ValueError, TypeError) as exc:
        diagnostic = failure_error(exc)["message"]
        try:
            audit = write_failure_record(exc, args.data, args.protocol, args.sources, output,
                                         started_at_utc=started)
        except (ReproducibilityError, OSError, KeyError, ValueError, TypeError) as audit_error:
            audit_message = f"失败审计记录写入失败：{failure_error(audit_error)['message']}\n"
        else:
            audit_message = f"失败审计记录：{audit}\n"
        parser.exit(2, f"未通过输入与复现检查：{diagnostic}\n{audit_message}")
    print(json.dumps({"task_id": "PF1966-UV-T1", "run_manifest": str(manifest_path),
                      "scientific_review_status": "review_required"}, ensure_ascii=False))
    print("仅为原表数值重放；实验、机理、量子计算及四基团普适排序均未验证。")


if __name__ == "__main__":
    main()
