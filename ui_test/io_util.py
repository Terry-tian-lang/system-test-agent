# -*- coding: utf-8 -*-
import json
import os
from typing import List

from ui_test.models import UICase

HEADERS = [
    "用例编号", "平台", "标题", "模块", "优先级", "标签", "服务",
    "接口", "UI状态", "操作步骤", "预期", "备注",
]


def write_json(path: str, cases: List[UICase]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in cases], f, ensure_ascii=False, indent=2)


def write_xlsx(path: str, cases: List[UICase]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        from openpyxl import Workbook
    except ImportError as e:
        raise SystemExit("缺少 openpyxl，请先 pip install openpyxl") from e
    wb = Workbook()
    ws = wb.active
    ws.title = "UI用例"
    ws.append(HEADERS)
    for c in cases:
        ws.append([
            c.case_id, c.platform, c.title, c.module, c.priority, c.tag, c.service,
            " | ".join(c.apis), c.ui_status, " | ".join(c.steps),
            ",".join(c.expect), c.note,
        ])
    wb.save(path)
