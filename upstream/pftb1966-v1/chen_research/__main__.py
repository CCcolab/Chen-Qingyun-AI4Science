import argparse
from pathlib import Path

from .uv_replay import ReproducibilityError, replay, write_outputs


def main():
    parser = argparse.ArgumentParser(description="重放陈庆云团队 1966 年论文表 1 的数值关系")
    parser.add_argument("--data", type=Path, default=Path("data/pftb1966_table1.csv"))
    parser.add_argument("--protocol", type=Path, default=Path("protocols/pftb1966_uv.json"))
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    try:
        result = replay(args.data, args.protocol)
        write_outputs(result, args.output)
    except (ReproducibilityError, OSError, KeyError, ValueError) as exc:
        parser.exit(2, f"未通过输入与复现检查：{exc}\n")
    print(result["task_id"], result["numerical_status"])
    print("仅为原表数值重放；实验、机理、量子计算及四基团普适排序均未验证。")


if __name__ == "__main__":
    main()
