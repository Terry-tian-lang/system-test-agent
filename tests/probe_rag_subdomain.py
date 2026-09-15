#!/usr/bin/env python3
"""针对 rag-func 子域 与 /runtime/console/api 前缀重新探测"""
import sys, time, ssl, re
import urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "output" / "rag_subdomain_probe.txt"
lines = []
def log(m=""):
    lines.append(m)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SAMPLE = "01234567-89ab-4def-8123-456789abcdef"

def probe(base, path, method="GET"):
    url = base + path
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Authorization": "Bearer invalid-token",
    }, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        body = resp.read().decode("utf-8", "ignore")[:80]
        return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:80]
        return e.code, body
    except Exception as e:
        return -1, str(e)[:60]

RAG = "http://rag-func.ibosssoft.com.cn"
MAIN = "http://ai-func.ibosssoft.com.cn"

log("=" * 70)
log("=== 1) rag-func 子域: 首页/健康 ===")
for p in ["/", "/health", "/api/health", "/console/api/features", "/v1/apps"]:
    code, body = probe(RAG, p)
    tag = "✅" if code in (200, 401, 403) else ("⚠️" if code in (405, 503) else "❌")
    log(f"{tag} [{code}] GET {p} -> {body!r}")
    time.sleep(0.1)

log("")
log("=" * 70)
log("=== 2) rag-func 子域: rag pipelines 接口 ===")
RAG_PATHS = [
    "/api/rag/pipelines",
    "/rag/pipelines",
    "/pipelines",
    "/api/pipelines",
    "/v1/pipelines",
    "/api/rag/pipeline/templates",
]
for p in RAG_PATHS:
    code, body = probe(RAG, p)
    tag = "✅" if code in (401, 403) else ("⚠️" if code in (405, 503) else "❌")
    log(f"{tag} [{code}] GET {p} -> {body!r}")
    time.sleep(0.1)

log("")
log("=" * 70)
log("=== 3) 主域名 /runtime/console/api 前缀 ===")
RUNTIME_PATHS = [
    "/runtime/console/api/apps",
    "/runtime/console/api/features",
    "/runtime/console/api/datasets",
    "/runtime/console/api/explore/apps",
    "/runtime/console/api/messages/{id}/more-like-this",
    "/runtime/api/apps",
]
for p in RUNTIME_PATHS:
    code, body = probe(MAIN, p)
    tag = "✅" if code in (401, 403) else ("⚠️" if code in (405, 503) else "❌")
    log(f"{tag} [{code}] GET {p} -> {body!r}")
    time.sleep(0.1)

log("")
log("=" * 70)
log("=== 4) rag-func 发现的首页资源（找 API 线索） ===")
code, body = probe(RAG, "/")
log(f"[{code}] GET / 首页 -> {body[:150]!r}")
# 提取首页中的 JS/链接
if code == 200 and "html" in body.lower() or code == 200:
    try:
        req = urllib.request.Request(RAG + "/", headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = resp.read().decode("utf-8", "ignore")
        logs = []
        for m in re.finditer(r'(?:src|href)="([^"]+)"', html)[:0] if False else re.finditer(r'(?:src|href)="([^"]+)"', html):
            logs.append(m.group(1))
        for l in logs[:20]:
            log(f"  资源: {l}")
        # 检查是否有 __NEXT_DATA__ 或配置
        cfg = re.findall(r'(next-public-[a-z\-]+|BASE_URL|baseUrl[^,]{0,60})', html)
        for c in cfg[:10]:
            log(f"  配置: {c}")
    except Exception as e:
        log(f"  拉取首页失败: {e}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))