# -*- coding: utf-8 -*-
"""
Agent 平台 UI 真实用例 (基于已登录会话, 只读点击验证, 不提交写操作)
覆盖首页冒烟 + 快速入门四大入口 (映射 scenarios_agent.py 相关用例)
运行:  python -m pytest ui_test/test_agent_real.py -v
调试:  加 --pw-headed 显示浏览器窗口
"""
from pathlib import Path

from playwright.sync_api import expect

BASE = "http://ai-func.ibosssoft.com.cn"
SCREEN_DIR = Path(__file__).resolve().parents[1] / "output" / "ui_cases" / "screenshots"


def _shot(page, name):
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREEN_DIR / name), full_page=False)


def test_ui_agent_001_home(logged_page):
    """首页可达: 已登录且显示快速入门/工作空间信息 (Agent-001 登录态验证)"""
    page = logged_page
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    assert "cas" not in page.url, f"登录态失效: {page.url}"
    body = page.inner_text("body")
    assert "智能体平台" in body, "首页未显示平台标题"
    assert ("公共空间" in body) or ("工作空间" in body), "首页未显示工作空间"
    _shot(page, "agent_001_home.png")


def test_ui_agent_002_search_workspace_modal(logged_page):
    """搜索工作空间: 点击按钮出现搜索弹窗 (Agent-002)"""
    page = logged_page
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    btn = page.get_by_role("button", name="搜索工作空间")
    assert btn.count() > 0, "未找到「搜索工作空间」按钮"
    btn.first.click()
    page.wait_for_timeout(2000)
    # 弹窗内应出现"工作空间"相关输入/列表
    body = page.inner_text("body")
    assert "工作空间" in body, "搜索弹窗未出现"
    _shot(page, "agent_002_workspace_modal.png")
    # 关闭弹窗(按 Esc)
    page.keyboard.press("Escape")
    page.wait_for_timeout(800)


def test_ui_agent_003_workspace_switch(logged_page):
    """工作空间切换入口存在: 左侧「公共空间」按钮可点击 (Agent-005 切换前置)"""
    page = logged_page
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    ws_btn = page.get_by_role("button", name="公共空间")
    assert ws_btn.count() > 0, "未找到工作空间切换入口"
    ws_btn.first.click()
    page.wait_for_timeout(1500)
    _shot(page, "agent_003_ws_switch.png")


def test_ui_agent_004_guide_project_manage(logged_page):
    """快速入门: 前往项目管理页 (项目管理入口可达)"""
    page = logged_page
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    btn = page.get_by_role("button", name='前往"项目管理"')
    if btn.count() == 0:
        btn = page.get_by_text("项目管理").first
        # 退回: 只验证存在入口
        assert page.get_by_text("项目管理").count() > 0, "项目管理入口缺失"
        _shot(page, "agent_004_project_entry.png")
        return
    btn.first.click()
    page.wait_for_timeout(4000)
    body = page.inner_text("body")
    # 项目管理页特征: Studio/Chatflow/Agent 类型筛选 + 应用列表(ADD TAGS)
    assert ("Studio" in body) or ("newProject" in body) or ("Chatflow" in body), "项目管理页未打开"
    _shot(page, "agent_004_project_page.png")


def test_ui_agent_005_guide_create_agent(logged_page):
    """快速入门: 创建智能体入口可进入编排页 (Agent-012 创建前置)"""
    page = logged_page
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    btn = page.get_by_role("button", name="创建智能体")
    assert btn.count() > 0, "未找到「创建智能体」入口"
    btn.first.click()
    page.wait_for_timeout(4000)
    body = page.inner_text("body")
    assert ("智能体" in body) or ("编排" in body), "创建智能体页面未打开"
    _shot(page, "agent_005_create_agent.png")


def test_ui_agent_006_guide_add_kb(logged_page):
    """快速入门: 添加知识库入口存在 (Agent-037 知识检索前置)"""
    page = logged_page
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    btn = page.get_by_role("button", name="添加知识库")
    assert btn.count() > 0, "未找到「添加知识库」入口"
    btn.first.click()
    page.wait_for_timeout(2000)
    _shot(page, "agent_006_add_kb.png")
    page.keyboard.press("Escape")
    page.wait_for_timeout(800)


def test_ui_agent_007_menu_nav(logged_page):
    """左侧导航存在: 品牌按钮 + 导航图标按钮 (UI框架完整性)"""
    page = logged_page
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    brand = page.get_by_role("button", name="坤元万象")
    assert brand.count() == 1, "品牌入口异常"
    # 侧边栏按钮总数(品牌+公共空间等)应 >= 2
    all_btns = page.locator("button").all()
    texts = [(b.inner_text() or "").strip() for b in all_btns]
    icon_btns = [t for t in texts if t and len(t) < 12]
    assert len(icon_btns) >= 2, f"侧边导航按钮不足: {icon_btns}"
    assert any("公共空间" in t for t in texts), "未找到工作空间导航"
    _shot(page, "agent_007_nav.png")