# -*- coding: utf-8 -*-
"""按用例生成 Playwright UI 脚本。"""
import argparse
import os
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from ui_test.case_builder import PLATFORMS, build_cases, load_scenarios
from ui_test.script_builder import render_script


def parse_platforms(name: str):
    if name == "all":
        return list(PLATFORMS)
    if name not in PLATFORMS:
        print(f"非法平台: {name}，合法值: agent|rag|shujuzhili|all", file=sys.stderr)
        sys.exit(2)
    return [name]


def load_page_map(plat: str) -> dict:
    path = os.path.join(ROOT, "ui_test", "page_maps", f"{plat}.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="生成 Playwright UI 脚本")
    ap.add_argument("--platform", required=True, help="agent|rag|shujuzhili|all")
    args = ap.parse_args(argv)

    gen_dir = os.path.join(ROOT, "ui_test", "generated")
    os.makedirs(gen_dir, exist_ok=True)
    failed = False
    for plat in parse_platforms(args.platform):
        try:
            scenarios = load_scenarios(plat)
            page_map = load_page_map(plat)
        except Exception as e:
            print(f"[{plat}] 加载失败: {e}", file=sys.stderr)
            failed = True
            continue
        cases = build_cases(plat, scenarios, has_home=True)
        src = render_script(plat, cases, page_map, source=f"scenarios_{plat}.py")
        out = os.path.join(gen_dir, f"test_{plat}_ui.py")
        with open(out, "w", encoding="utf-8") as f:
            f.write(src)
        print(f"[{plat}] 脚本 → {out} （1 条冒烟 + {len(cases)} 条 skip/占位）")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
