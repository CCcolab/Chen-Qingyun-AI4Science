"""Verify this research package and the identity of its executed result."""

import hashlib
import json
import sys
from pathlib import Path, PurePosixPath


def verify():
    root = Path(__file__).resolve().parents[1]
    expected = {}
    for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        checksum, name = line.split("  ", 1)
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts or name in expected:
            raise ValueError("校验清单含非法路径或重复项")
        file = root / name
        if not file.is_file() or file.is_symlink():
            raise ValueError(f"缺文件或符号链接：{name}")
        if hashlib.sha256(file.read_bytes()).hexdigest() != checksum:
            raise ValueError(f"文件内容与交付清单不符：{name}")
        expected[name] = checksum
    ignored = {"scratch", "__pycache__", ".git"}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
              and not (set(p.relative_to(root).parts) & ignored) and p.name != "SHA256SUMS"
              and p.suffix not in {".pyc", ".pyo"}}
    if actual != set(expected):
        raise ValueError("交付成员与清单不一致")
    result = json.loads((root / "results/pftb1966-uv-replay.json").read_text(encoding="utf-8"))
    for key, name in [("data_sha256", "data/pftb1966_table1.csv"),
                      ("protocol_sha256", "protocols/pftb1966_uv.json"),
                      ("code_sha256", "chen_research/uv_replay.py")]:
        if result[key] != expected[name]:
            raise ValueError("已执行结果与当前输入／代码身份不一致")
    candidate = json.loads((root / "results/website-candidate.json").read_text(encoding="utf-8"))
    if candidate["publication_status"] != "review_required":
        raise ValueError("本包结果不应越过科学审阅")
    for name in ("reaction_mechanism", "free_anion_detection", "universal_four_group_order"):
        if result["boundaries"][name] != "not_tested":
            raise ValueError("数值重放不能升级为未执行的科学验证")
    print(f"Integrity and result-identity checks passed: {len(expected)} files.")


if __name__ == "__main__":
    try:
        verify()
    except (OSError, ValueError, KeyError) as exc:
        print(f"交付核验未通过：{exc}", file=sys.stderr)
        raise SystemExit(1)
