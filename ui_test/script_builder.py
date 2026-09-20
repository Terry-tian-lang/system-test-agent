# -*- coding: utf-8 -*-
"""把用例 + 页面地图渲染成 Playwright pytest 源码。"""
from datetime import datetime
from typing import Any, Dict, List

from ui_test.models import UICase


def render_script(platform: str, cases: List[UICase], page_map: Dict[str, Any], source: str) -> str:
    base = (page_map.get("base_url") or "").rstrip("/")
    smoke = page_map.get("smoke") or {}
    smoke_path = smoke.get("path") or "/"
    url = base + (smoke_path if smoke_path.startswith("/") else "/" + smoke_path)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    skip_fns = []
    for c in cases:
        if c.ui_status == "skip_known_gap":
            reason = "已知缺口"
        elif c.ui_status == "pending_selector":
            reason = "待补选择器"
        else:
            reason = "第一刀仅跑首页冒烟"
        fn = "test_" + c.case_id.replace("-", "_")
        skip_fns.append(
            f"@pytest.mark.skip(reason={reason!r})\n"
            f"def {fn}():\n"
            f"    assert True  # {c.case_id} {c.title}\n"
        )

    skip_block = "\n".join(skip_fns)
    return f'''# -*- coding: utf-8 -*-
# 自动生成, 勿手改。生成时间: {ts}  来源: {source}
# 平台: {platform}  冒烟: {url}

import os
import pytest

SCREEN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "output", "ui_cases", "screenshots")


def test_smoke_{platform}_home():
    """打开 {platform} 站点入口, 断言页面存在 html。"""
    from playwright.sync_api import sync_playwright

    headed = os.environ.get("PW_HEADED", "") == "1"
    os.makedirs(SCREEN_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        page = browser.new_page()
        try:
            page.goto({url!r}, timeout=20000, wait_until="domcontentloaded")
            assert page.locator("html").count() > 0
        except Exception:
            page.screenshot(path=os.path.join(SCREEN_DIR, "smoke_{platform}.png"))
            raise
        finally:
            browser.close()


{skip_block}
'''
