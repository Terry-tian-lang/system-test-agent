#!/usr/bin/env python3
"""深度侦察：下载 JS chunk，提取 API 端点模式与框架指纹"""
import sys, re, ssl, json, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TARGET = "http://ai-func.ibosssoft.com.cn"
OUT = ROOT / "output" / "probe_js.txt"
lines = []
def log(m=""):
    lines.append(m)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Referer": TARGET + "/explore/apps",
    })
    return urllib.request.urlopen(req, timeout=timeout, context=ctx).read().decode("utf-8", "ignore")

# 1) 从首页 HTML 提取所有 JS chunk 路径
html = (ROOT / "output" / "system_home.html").read_text(encoding="utf-8", errors="ignore")
js_paths = re.findall(r'src=["\'](/_next/static/[^"\']+\.js)["\']', html)
js_paths = list(dict.fromkeys(js_paths))
log(f"发现 {len(js_paths)} 个 JS chunk")

# 2) 对主要 chunk 分析
API_PATTERNS = [
    (r'/console/api/[a-zA-Z0-9_\-/{}]+', "console-api"),
    (r'/console/api/apps', "apps-api"),
    (r'/v1/[a-zA-Z0-9_\-/{}]+', "v1-api"),
    (r'/features/[a-zA-Z0-9_\-/{}]+', "features-api"),
    (r'fetch\(["\'`]([^"\'`]+)["\'`]', "fetch-call"),
    (r'axios[^;]{0,80}["\'`]([^"\'`]+)["\'`]', "axios-call"),
]
API_ENDPOINTS = set()
FRAMEWORK = set()
APP_ID_HINT = set()

for i, js in enumerate(js_paths):
    url = TARGET + js
    try:
        code = fetch(url)
    except Exception as e:
        log(f"  下载失败 {js}: {e}")
        continue

    # 框架指纹
    if "dify" in code.lower():
        FRAMEWORK.add("dify")
        APP_ID_HINT.update(re.findall(r'app[_\-]?id["\']?\s*[:=]\s*["\']?([a-z0-9\-]{20,})["\']?', code))
    if "langchain" in code.lower(): FRAMEWORK.add("langchain")
    if "faiss" in code.lower(): FRAMEWORK.add("faiss")
    if "api/chat-messages" in code: FRAMEWORK.add("dify-service-api")
    if "api/conversations" in code: FRAMEWORK.add("dify-conversation-api")

    # API 端点提取
    for pat, tag in API_PATTERNS:
        for m in re.finditer(pat, code):
            ep = m.group(1) if m.lastindex else m.group(0)
            ep = ep.split("?")[0]
            if len(ep) > 3:
                API_ENDPOINTS.add(f"{tag}: {ep}")

    if i < 5 or len(code) > 200_000:
        log(f"  [{i}] {js} ({len(code)} chars)")

# 3) 输出
log("")
log("=== 框架指纹 ===")
log(f"  {sorted(FRAMEWORK) if FRAMEWORK else '(未识别)'}")
if APP_ID_HINT:
    log(f"  app_id 样本: {sorted(APP_ID_HINT)[:3]}")

log("")
log(f"=== API 端点 ({len(API_ENDPOINTS)}) ===")
for ep in sorted(API_ENDPOINTS):
    log(f"  {ep}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))