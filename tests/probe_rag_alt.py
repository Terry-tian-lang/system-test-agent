#!/usr/bin/env python3
"""探测 rag_pipelines / conversations 接口的替代前缀"""
import sys, time, ssl, re
import urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TARGET = "http://ai-func.ibosssoft.com.cn"
OUT = ROOT / "output" / "rag_alt_probe.txt"
lines = []
def log(m=""):
    lines.append(m)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SAMPLE = "01234567-89ab-4def-8123-456789abcdef"

def probe(path):
    url = TARGET + path
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Authorization": "Bearer invalid-token",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        body = resp.read().decode("utf-8", "ignore")[:80]
        return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:80]
        return e.code, body
    except Exception as e:
        return -1, str(e)[:60]

# 候选前缀组合
PREFIXES = ["", "/api", "/rag", "/rag/api", "/rag-api", "/v1", "/console"]
PATHS = [
    "/rag/pipelines",
    "/pipelines",
    "/rag/pipelines/{id}/workflows/published/run",
    "/console/api/messages/{id}/more-like-this",
    "/console/api/saved-messages",
    "/console/api/conversations",
    "/console/api/chat-messages",
]

log("=== rag/pipelines 替代前缀探测 ===")
for p in PATHS:
    for pre in PREFIXES:
        path = (pre + p).replace("//", "/")
        code, body = probe(path)
        # 只打印非404结果
        if code != 404:
            tag = "✅" if code in (401, 403) else ("⚠️" if code in (405, 503) else "🟢")
            log(f"{tag} [{code}] GET {path} -> {body!r}")
        time.sleep(0.1)

log("")
log("=== 另测: 主域名根路径重定向行为 ===")
for root in ["/", "/rag", "/console", "/api"]:
    code, body = probe(root)
    log(f"  [{code}] GET {root} -> {body[:60]!r}")

log("")
log("=== 检查 /explore/apps 是否引用 rag 域名 ===")
html = (ROOT / "output" / "system_home.html").read_text(encoding="utf-8", errors="ignore")
for m in re.finditer(r'https?://[a-zA-Z0-9\.\-]*ibosssoft[a-zA-Z0-9\.\-/]*', html):
    log(f"  HTML含: {m.group(0)}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines) if lines else "done")