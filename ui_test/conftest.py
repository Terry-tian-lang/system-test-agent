# -*- coding: utf-8 -*-
"""Agent UI 自动化 conftest: 登录 fixture (复用已保存会话, 失效则重新 CAS 登录)"""
import io
import os
import sys
from pathlib import Path

import pytest

# 注意: 不要替换 sys.stdout —— 会破坏 pytest 的 capture 机制

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "ui_cases"
OUT.mkdir(parents=True, exist_ok=True)
STATE = OUT / "agent_state.json"

BASE = "http://ai-func.ibosssoft.com.cn"
CAS_LOGIN = ("http://cas-func.ibosssoft.com.cn/cas/login?service="
             "http%3A%2F%2Fai-func.ibosssoft.com.cn%2Fconsole%2Fapi%2Flogin-call-back"
             "%3Fback_url%3Dhttp%3A%2F%2Fai-func.ibosssoft.com.cn%2Fhome")


def _read_env() -> dict:
    env = {}
    env_path = ROOT / ".env"
    if not env_path.exists():
        return env
    text = env_path.read_text(encoding="utf-8", errors="replace")
    if "\ufffd" in text:
        text = env_path.read_text(encoding="gbk", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def cas_login(page) -> None:
    """在 CAS 登录页用 .env 账号登录"""
    env = _read_env()
    email = env.get("AGENT_UI_EMAIL", "")
    password = env.get("AGENT_UI_PASSWORD", "")
    assert email and password, ".env 缺少 AGENT_UI_EMAIL / AGENT_UI_PASSWORD"
    page.goto(CAS_LOGIN, timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    if page.locator("#email").count() == 0:
        return  # 已登录
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type=submit].login-btn")
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    page.wait_for_timeout(6000)
    assert "cas" not in page.url, f"CAS 登录失败: {page.url}"


def ensure_login(ctx) -> None:
    """确保浏览器上下文已登录 ai-func (复用/新建会话)"""
    if STATE.exists():
        try:
            ctx.storage_state(path=str(STATE))  # 载入
        except Exception:
            pass
    page = ctx.new_page()
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    if "cas" in page.url or page.locator("#email").count() > 0:
        # 会话失效 -> CAS 重新登录
        cas_login(page)
        ctx.storage_state(path=str(STATE))
    page.close()


def pytest_addoption(parser):
    parser.addoption("--pw-headed", action="store_true", default=False,
                     help="显示浏览器窗口(调试用)")


def pytest_configure(config):
    os.environ.setdefault("PW_HEADED", "1" if config.getoption("--pw-headed") else "")


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    b = pw.chromium.launch(headless=os.environ.get("PW_HEADED", "") != "1")
    yield b
    b.close()
    pw.stop()


@pytest.fixture(scope="session")
def logged_page(browser):
    """已登录 ai-func 的页面 (会话失效自动重登)"""
    ctx = browser.new_context()
    ensure_login(ctx)
    page = ctx.new_page()
    page.goto(BASE + "/home", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    assert "cas" not in page.url, f"登录态无效: {page.url}"
    yield page
    ctx.close()


@pytest.fixture()
def fresh_page(browser):
    """每用例独立上下文(共享已保存会话)"""
    ctx = browser.new_context(storage_state=str(STATE) if STATE.exists() else None)
    page = ctx.new_page()
    yield page
    ctx.close()