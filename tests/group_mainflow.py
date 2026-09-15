#!/usr/bin/env python3
"""按模块分组查看全部主流程用例(截断长文本)"""
import sys, json
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "output" / "mainflow_grouped.txt"
lines = []
def log(m=""):
    lines.append(m)

data = json.loads((ROOT / "output" / "mainflow_full.json").read_text(encoding="utf-8"))

# 按平台+模块分组
from collections import defaultdict
groups = defaultdict(list)
for c in data:
    groups[(c["platform"], c["模块"])].append(c)

log("=== 主流程用例分组 ===")
log("")
for (plat, mod), cases in groups.items():
    log(f"## [{plat}] {mod} ({len(cases)}条)")
    for c in cases:
        title = (c["用例标题"] or "").replace("\n", " ")
        steps = (c["操作步骤"] or "").replace("\n", " | ")
        log(f"  {c['用例编号']} [{c['优先级']}] {title}")
        log(f"    步骤: {steps[:160]}")
        log(f"    预期: {(c['实际结果'] or '').replace(chr(10), ' | ')[:120]}")
    log("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("done")