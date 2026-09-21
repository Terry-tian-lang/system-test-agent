# -*- coding: utf-8 -*-
"""
UI 自动化 conftest: 双环境 (test/prod) 自动切换
================================================
环境模型:
  test  测试环境  CAS=cas-func.ibosssoft.com.cn   账号 pbw@163.com   平台 ai-func (Agent)
  prod  生产环境  CAS=cas.bosssoft.com.cn         账号 tianyu@123.com 平台 rag.bosssoft.com.cn (RAG)

用法:
  python -m pytest ui_test/test_agent_real.py -v --env test --platform agent
  python -m pytest ui_test/test_rag_real.py    -v --env prod --platform rag
默认 env=test, platform=agent (向后兼容旧命令)

会话文件按 {env}_{platform} 区分: output/ui_cases/agent_state.json (test/agent) 等。
"""
import os
import sys
from pathlib import Path

import pytest

# 注意: 不要替换 sys.stdout —— 会破坏 pytest 的 capture 机制

ROOT = Path(__file__).resolve().parents[1]
# 确保 ui_test 包目录可导入 (pytest 收集 conftest 时可能尚未加入 sys.path)
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from env_config import get_env

OUT = ROOT / "output" / "ui_cases"
OUT.mkdir(parents=True, exist_ok=True)


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


def _cas_url(env_cfg: dict, platform_cfg: dict) -> str:
    """拼接 CAS 登录地址: cas_login?service=<callback>?back_url=<back_url> (URL编码)"""
    import urllib.parse
    service = platform_cfg["callback"] + "?back_url=" + platform_cfg["back_url"]
    return env_cfg["cas_login"] + "?service=" + urllib.parse.quote(service, safe="")


def resolve_config(env_name: str, platform: str) -> dict:
    """返回 {env, platform, cas_login, base_url, callback, back_url, state_path, email, password}"""
    env_cfg = get_env(env_name)
    if platform not in env_cfg["platforms"]:
        raise KeyError(f"环境 {env_name} 未配置平台 {platform}, 可用: {list(env_cfg['platforms'])}")
    p = env_cfg["platforms"][platform]
    envvars = _read_env()
    email = envvars.get(env_cfg["email_key"], "")
    password = envvars.get(env_cfg["password_key"], "")
    if not email or not password:
        raise RuntimeError(
            f".env 缺少 {env_cfg['email_key']} / {env_cfg['password_key']} "
            f"(环境={env_name} 平台={platform})")
    return {
        "env": env_name,
        "platform": platform,
        "env_name": env_cfg["name"],
        "cas_login": env_cfg["cas_login"],
        "cas_url": _cas_url(env_cfg, p),
        "base_url": p["base_url"],
        "home_path": p.get("home_path", "/home"),
        "callback": p["callback"],
        "back_url": p["back_url"],
        "state_path": str(OUT / p["state_file"]),
        "state_file": p["state_file"],
        "email": email,
        "password": password,
    }


def cas_login(page, cfg: dict) -> None:
    """在 CAS 登录页登录 (账号来自 .env, 按环境切换)"""
    page.goto(cfg["cas_url"], timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    if page.locator("#email").count() == 0:
        return  # 已登录
    page.fill("#email", cfg["email"])
    page.fill("#password", cfg["password"])
    page.click("button[type=submit].login-btn")
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    page.wait_for_timeout(6000)
    assert "cas" not in page.url, f"CAS 登录失败: {page.url} (环境={cfg['env']} 平台={cfg['platform']})"


def ensure_login(ctx, cfg: dict) -> None:
    """确保浏览器上下文已登录目标平台 (复用/新建会话)"""
    state_path = cfg["state_path"]
    if Path(state_path).exists():
        try:
            ctx.storage_state(path=state_path)  # 载入
        except Exception:
            pass
    page = ctx.new_page()
    page.goto(cfg["base_url"] + cfg["home_path"], timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    if "cas" in page.url or page.locator("#email").count() > 0:
        # 会话失效 -> CAS 重新登录
        cas_login(page, cfg)
        try:
            ctx.storage_state(path=state_path)
        except Exception:
            pass
    page.close()


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="test",
                     choices=["test", "prod"], help="运行环境: test(测试) / prod(生产)")
    parser.addoption("--platform", action="store", default="agent",
                     help="目标平台: agent / rag / shujuzhili")
    parser.addoption("--pw-headed", action="store_true", default=False,
                     help="显示浏览器窗口(调试用)")


def pytest_configure(config):
    os.environ.setdefault("PW_HEADED", "1" if config.getoption("--pw-headed") else "")
    os.environ["UI_ENV"] = config.getoption("--env")
    os.environ["UI_PLATFORM"] = config.getoption("--platform")


@pytest.fixture(scope="session")
def ui_cfg(request):
    """当前环境+平台配置 (含认证信息), 全 session 共享"""
    env = request.config.getoption("--env")
    platform = request.config.getoption("--platform")
    return resolve_config(env, platform)


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    b = pw.chromium.launch(headless=os.environ.get("PW_HEADED", "") != "1")
    yield b
    b.close()
    pw.stop()


@pytest.fixture(scope="session")
def logged_page(browser, ui_cfg):
    """已登录目标平台的页面 (会话失效自动重登)"""
    ctx = browser.new_context()
    ensure_login(ctx, ui_cfg)
    page = ctx.new_page()
    page.goto(ui_cfg["base_url"] + ui_cfg["home_path"], timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)
    assert "cas" not in page.url, f"登录态无效: {page.url} (环境={ui_cfg['env']})"
    yield page
    ctx.close()


@pytest.fixture()
def fresh_page(browser, ui_cfg):
    """每用例独立上下文(共享已保存会话)"""
    state_path = ui_cfg["state_path"]
    ctx = browser.new_context(storage_state=str(state_path) if Path(state_path).exists() else None)
    page = ctx.new_page()
    yield page
    ctx.close()