# -*- coding: utf-8 -*-
"""
RAG 平台 (生产环境) UI 真实用例
================================
基于已登录会话 (rag_state_prod.json), 只读点击验证:
  首页可达 / 知识库列表 / 数据库频道 / 搜索工作空间 / 创建知识库入口
映射 scenarios_rag.py 的 RAG-001/002/012 等前置用例

运行:
  python -m pytest ui_test/test_rag_real.py -v --env prod --platform rag
调试:
  python -m pytest ui_test/test_rag_real.py -v --env prod --platform rag --pw-headed
"""
from pathlib import Path

SCREEN_DIR = Path(__file__).resolve().parents[1] / "output" / "ui_cases" / "screenshots"


def _shot(page, name):
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREEN_DIR / name), full_page=False)


def test_ui_rag_001_home(logged_page, ui_cfg):
    """首页可达: 登录后显示知识库平台首页 (RAG-001 登录态)"""
    page = logged_page
    page.goto(ui_cfg["base_url"] + "/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    assert "cas" not in page.url, f"登录态失效: {page.url}"
    body = page.inner_text("body")
    assert "知识库" in body, "首页未显示知识库相关内容"
    assert ("快速入门" in body) or ("平台" in body), "首页未显示平台标识"
    _shot(page, "rag_001_home.png")


def test_ui_rag_002_datasets_list(logged_page, ui_cfg):
    """知识库列表页: 显示知识库条目与导入入口 (RAG-012 前置)"""
    page = logged_page
    page.goto(ui_cfg["base_url"] + "/datasets", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)
    body = page.inner_text("body")
    assert "知识库" in body, "知识库页未打开"
    assert "导入" in body, "未找到导入入口"
    _shot(page, "rag_002_datasets.png")


def test_ui_rag_003_database_channel(logged_page, ui_cfg):
    """数据库频道: 侧边数据库导航可点击并打开 (数据库页可达)"""
    page = logged_page
    page.goto(ui_cfg["base_url"] + "/datasets", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    btn = page.get_by_text("数据库").first
    assert btn.count() > 0, "未找到数据库导航"
    btn.click()
    page.wait_for_timeout(4000)
    body = page.inner_text("body")
    assert len(body.strip()) > 50, "数据库频道未加载内容"
    _shot(page, "rag_003_database.png")


def test_ui_rag_004_search_workspace(logged_page, ui_cfg):
    """搜索工作空间: 首页按钮出现搜索弹窗 (RAG-002 前置)"""
    page = logged_page
    page.goto(ui_cfg["base_url"] + "/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    btn = page.get_by_role("button", name="搜索工作空间")
    if btn.count() == 0:
        btn = page.get_by_text("搜索工作空间").first
    assert btn.count() > 0, "未找到「搜索工作空间」按钮"
    btn.first.click()
    page.wait_for_timeout(2000)
    body = page.inner_text("body")
    assert "工作空间" in body, "搜索弹窗未出现"
    _shot(page, "rag_004_search_ws.png")
    page.keyboard.press("Escape")
    page.wait_for_timeout(800)


def test_ui_rag_005_create_kb_entry(logged_page, ui_cfg):
    """创建知识库入口: 首页「创建知识库」按钮可进入创建流程 (RAG-012 前置)"""
    page = logged_page
    page.goto(ui_cfg["base_url"] + "/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    btn = page.get_by_role("button", name="创建知识库")
    if btn.count() == 0:
        btn = page.get_by_text("创建知识库").first
    assert btn.count() > 0, "未找到「创建知识库」入口"
    btn.first.click()
    page.wait_for_timeout(3000)
    body = page.inner_text("body")
    assert "知识库" in body, "创建知识库页面未打开"
    _shot(page, "rag_005_create_kb.png")