#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 RAG 接口主流程回归场景: scenarios_rag_mainflow.py
数据来源:
  - Excel 主流程用例 (权威): C:\\Users\\Admin\\Desktop\\需求\\主流程\\知识库平台-主流程回归测试用例.xlsx
  - 接口映射 (已验证真实路由): api_test/scenarios_rag.py (steps)
输出: api_test/scenarios_rag_mainflow.py (按 Excel 顺序, 含前置条件/步骤说明)
"""
import io, json, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"D:\测试专用-deepseek\system-test-agent")
XLSX = r"C:\Users\Admin\Desktop\需求\主流程\知识库平台-主流程回归测试用例.xlsx"
API_SCEN = ROOT / "api_test" / "scenarios_rag.py"
OUT = ROOT / "api_test" / "scenarios_rag_mainflow.py"

# ---- 1) 读 Excel 元数据 (主流程用例权威来源) ----
from openpyxl import load_workbook
wb = load_workbook(XLSX, data_only=True)
ws = wb["功能测试用例"]
excel = {}
for row in ws.iter_rows(min_row=2, values_only=True):
    if not row or not row[1]:
        continue
    cid = str(row[1]).strip()
    excel[cid] = {
        "seq": row[0], "module": row[2] or "", "priority": row[3] or "",
        "type": row[4] or "", "title": row[5] or "",
        "precondition": row[6] or "", "steps": row[7] or "", "expect": row[8] or "",
    }
print(f"Excel 读取: {len(excel)} 条主流程用例")

# ---- 2) 读现有接口场景 ----
sys.path.insert(0, str(ROOT / "api_test"))
import scenarios_rag as sr
api_scen = dict(sr.SCENARIOS)

# ---- 3) 按 Excel 顺序合并 ----
ordered = []
missing_ok = []
for cid in sorted(excel, key=lambda k: excel[k]["seq"]):
    e = excel[cid]
    title = e["title"]
    module = e["module"]
    priority = e["priority"]
    pre = (e["precondition"] or "").replace("\n", " ") or "—"
    op = (e["steps"] or "").replace("\n", " ") or "—"
    exp = (e["expect"] or "").replace("\n", " ") or "—"

    src = api_scen.get(cid)
    if src is None:
        missing_ok.append(cid)
        steps = []
        tag = "UI"
    else:
        steps = src.get("steps") or []
        # 从现有步骤派生: 若无 steps 且非纯UI, 补占位说明
        tag = src.get("tag") or "API"
        if not steps:
            tag = "UI"

    case = {
        "title": title,
        "module": module,
        "priority": priority,
        "platform": "rag",
        "service": "ragflow",
        "tag": tag,
        # 主流程元数据 (Excel): 前置条件/操作步骤/预期
        "note": f"前置: {pre} | Excel步骤: {op} | 预期: {exp}",
        "steps": steps,
    }
    ordered.append((cid, case))

# ---- 4) 写文件 ----
body = []
body.append('# -*- coding: utf-8 -*-')
body.append('"""')
body.append('RAG 接口主流程回归场景 (RAG-001~057, 共 %d 条)  数据来源: 知识库平台-主流程回归测试用例.xlsx' % len(ordered))
body.append('由 tools/gen_rag_mainflow_scenarios.py 生成, 勿手改; 需重新生成请运行该脚本。')
body.append('每条用例携带 Excel 前置条件/操作步骤/预期(note) 与已验证的真实接口步骤(steps)。')
body.append('"""')
body.append('from pathlib import Path')
body.append('')
body.append('THIS_DIR = Path(__file__).parent')
body.append('SCENARIOS = {')

for cid, case in ordered:
    lines = [f'    {cid!r}: {{']
    for k, v in case.items():
        lines.append(f'        {k!r}: {v!r},')
    lines.append('    },')
    body.append('\n'.join(lines))

body.append('}')
body.append('')
body.append(f'# 共 {len(ordered)} 条 (Excel 主流程 57 条)  |  纯UI/无接口映射: {missing_ok if missing_ok else "无"}')

OUT.write_text('\n'.join(body), encoding="utf-8")
print(f"已生成 {OUT}: {len(ordered)} 条 (Excel 顺序)")
print(f"纯UI/无接口映射用例: {missing_ok if missing_ok else '无'}")