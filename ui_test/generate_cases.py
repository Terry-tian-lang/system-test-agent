# -*- coding: utf-8 -*-
"""按接口/场景生成 UI 测试用例 (JSON + Excel)。"""
import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from ui_test.case_builder import PLATFORMS, build_cases, load_scenarios
from ui_test.io_util import write_json, write_xlsx


def parse_platforms(name: str):
    if name == "all":
        return list(PLATFORMS)
    if name not in PLATFORMS:
        print(f"非法平台: {name}，合法值: agent|rag|shujuzhili|all", file=sys.stderr)
        sys.exit(2)
    return [name]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="生成 UI 测试用例")
    ap.add_argument("--platform", required=True, help="agent|rag|shujuzhili|all")
    args = ap.parse_args(argv)

    out_dir = os.path.join(ROOT, "output", "ui_cases")
    failed = False
    for plat in parse_platforms(args.platform):
        try:
            scenarios = load_scenarios(plat)
        except Exception as e:
            print(f"[{plat}] 场景加载失败: {e}", file=sys.stderr)
            failed = True
            continue
        if not scenarios:
            print(f"[{plat}] 场景为空，跳过", file=sys.stderr)
            failed = True
            continue
        cases = build_cases(plat, scenarios, has_home=True)
        json_path = os.path.join(out_dir, f"{plat}_cases.json")
        xlsx_path = os.path.join(out_dir, f"{plat}_cases.xlsx")
        write_json(json_path, cases)
        write_xlsx(xlsx_path, cases)
        print(f"[{plat}] {len(cases)} 条 → {json_path}")
        print(f"[{plat}] Excel → {xlsx_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
