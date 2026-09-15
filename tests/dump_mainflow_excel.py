#!/usr/bin/env python3
"""读取主流程回归测试用例 Excel 结构"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "output" / "mainflow_excel_dump.txt"
lines = []
def log(m=""):
    lines.append(m)

from openpyxl import load_workbook

files = [
    r"C:\Users\Admin\Desktop\需求\主流程\智能体平台开发态-主流程回归测试用例.xlsx",
    r"C:\Users\Admin\Desktop\需求\主流程\知识库平台-主流程回归测试用例.xlsx",
]

for f in files:
    log("=" * 80)
    log(f"FILE: {Path(f).name}")
    wb = load_workbook(f, data_only=True)
    log(f"SHEETS: {wb.sheetnames}")
    for sn in wb.sheetnames:
        ws = wb[sn]
        log(f"--- sheet: {sn}  ({ws.max_row}行 x {ws.max_column}列) ---")
        # 表头
        hdr = [str(ws.cell(1, c).value or "") for c in range(1, ws.max_column + 1)]
        log(f"表头: {hdr}")
        # 打印前5行数据(非空)
        shown = 0
        for r in range(2, ws.max_row + 1):
            row = [str(ws.cell(r, c).value or "") for c in range(1, ws.max_column + 1)]
            if any(v.strip() for v in row):
                log(f"  R{r}: " + " | ".join(v[:40] for v in row))
                shown += 1
                if shown >= 6:
                    log(f"  ... 共 {ws.max_row - 1} 数据行")
                    break
        log("")
    log("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("done")