#!/usr/bin/env python3
"""验证 rag-func (RagFlow) 子域的真实 API"""
import sys, time, ssl, re
import urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

RAG = "http://rag-func.ibosssoft.com.cn"
OUT = ROOT / "output" / "ragflow_api_probe.txt"
lines = []
def log(m=""):
    lines.append(m)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def probe(path, method="GET", token=False):
    h = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    if token:
        h["Authorization"] = "Bearer invalid-token-for-probe"
    req = urllib.request.Request(RAG + path, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        body = resp.read().decode("utf-8", "ignore")[:100]
        return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:100]
        return e.code, body
    except Exception as e:
        return -1, str(e)[:60]

log("=" * 70)
log("=== RagFlow 标准 API 前缀探测 (未认证) ===")
# RagFlow OpenAPI: /api/v1/..., 自带 ui_api: /api/...
PATHS = [
    "/api/v1/datasets",            # 数据集列表
    "/api/v1/chats",               # 聊天
    "/api/v1/documents/1",
    "/api/v1/users/info",
    "/api/v1/pipelines",
    "/api/v1/agents",
    "/api/new_token",              # 前端登录
    "/api/token_list",
    "/api/user_setting",           # (可能是 /api/user/setting)
    "/api/dataset",
    "/api/dataset/list",
    "/api/completion",             # chat completion
    "/api/conversation",
    "/api/new_conversation",
    "/api/document/list",
    "/api/document/thumbnails",
    "/api/file2document/convert",
    "/api/user/login",
    "/api/v1/user/login",
    "/v1/datasets",
]
for p in PATHS:
    code, body = probe(p)
    if code == 404 and '"code":100' in body:
        tag = "❌"
    elif code in (401, 403):
        tag = "✅"   # 需认证但存在
    elif code == 200:
        tag = "🟢"
    elif code in (405, 422):
        tag = "⚠️"
    else:
        tag = "❓"
    log(f"{tag} [{code}] {p} -> {body!r}")
    time.sleep(0.1)

log("")
log("=== 带 Token 再试关键端点 ===")
for p in ["/api/v1/datasets", "/api/v1/chats", "/api/v1/users/info"]:
    code, body = probe(p, token=True)
    tag = "✅" if code in (401, 403) else ("🟢" if code == 200 else "❌")
    log(f"{tag} [{code}] Bearer {p} -> {body!r}")
    time.sleep(0.1)

log("")
log("=== umi.js 中 fetch/axios 调用模式 (含完整前缀) ===")
umi = (ROOT / "output" / "rag_chunks" / "umi.5f3c50bb.js").read_text(encoding="utf-8", errors="ignore")
# 找 base url 变量定义
for m in re.finditer(r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*["\']([^"\']*api[^"\']*)["\']', umi):
    log(f"  var {m.group(1)} = {m.group(2)!r}")

# 找 API_PREFIX 类配置
for m in re.finditer(r'["\']([^"\']*(?:prefix|PREFIX)[^"\']*)["\']\s*[:=]\s*["\']([^"\']+)["\']', umi):
    log(f"  prefix: {m.group(1)} = {m.group(2)!r}")

# fetch(`/api/...) 完整模式 (允许模板变量)
api_calls = set()
for m in re.finditer(r'fetch\(`?["\']?(/api/[a-zA-Z0-9_\-/\$\{\}\.`]*)', umi):
    api_calls.add(m.group(1))
log(f"\n  fetch(/api/...) 调用 ({len(api_calls)}):")
for c in sorted(api_calls)[:40]:
    log(f"    {c}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))