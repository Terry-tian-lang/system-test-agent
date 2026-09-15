#!/usr/bin/env python3
"""确认 API 网关行为：探测各种前缀的端点可达性"""
import sys, re, ssl, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TARGET = "http://ai-func.ibosssoft.com.cn"
OUT = ROOT / "output" / "probe_gateway.txt"
lines = []
def log(m=""):
    lines.append(m)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def probe(path, method="GET", headers=None, body=None):
    url = TARGET + path
    h = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
    if headers: h.update(headers)
    data = body.encode("utf-8") if body else None
    if data:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return resp.status, (resp.read().decode("utf-8", "ignore")[:200])
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode("utf-8", "ignore")[:200])
    except Exception as e:
        return "ERR", str(e)[:150]

# 1) 从缓存 JS 找 hy 变量的真实定义与 next-public 注入
log("=== 下一步：寻找真实 API base (hy 变量来源) ===")
js_dir = ROOT / "output" / "js_chunks"
if js_dir.exists():
    for f in js_dir.glob("*.js"):
        code = f.read_text(encoding="utf-8", errors="ignore")
        for pat in [r'["\']next-public-rag-base-url["\']\s*,\s*["\']([^"\']+)["\']',
                    r'["\']next-public-cas-base-url["\']\s*,\s*["\']([^"\']+)["\']',
                    r'["\']hy["\']\s*:\s*["\']([^"\']+)["\']',
                    r'hy=\w+\(?["\']?([^"\')]+)["\']?\)?']:
            for m in re.finditer(pat, code):
                val = m.group(1)
                if "http" in val or val.startswith("/"):
                    log(f"  {f.name}: {val}")
for pat, tag in [(r'next-public-cas-base-url', "CAS_URL"), (r'next-public-rag-base-url', "RAG_URL")]:
    pass

# 2) 探测常见前缀
log("")
log("=== 探测 API 前缀 ===")
probes = [
    # 标准 Dify console API
    ("/console/api/setup", "GET"),          # Dify 安装检查
    ("/console/api/apps", "GET"),           # 应用列表
    ("/console/api/features", "GET"),
    ("/console/api/workspaces/current", "GET"),
    # 网关/健康
    ("/health", "GET"),
    ("/api/health", "GET"),
    ("/webhook", "POST"),
    # v1 服务 API
    ("/v1/apps", "GET"),
    # 网关前缀
    ("/api/console/apps", "GET"),
    ("/rag/console/api/apps", "GET"),
    # 刷新 token 端点 (在前面 JS 中发现 ${r.hy}/refresh-token)
    ("/refresh-token", "GET"),
    ("/console/refresh-token", "GET"),
    ("/api/refresh-token", "GET"),
    # CAS
    ("/cas/v1/tickets", "GET"),
    ("/auth/login", "GET"),
]
for path, method in probes:
    code, resp_body = probe(path, method)
    status_text = str(code)
    mark = "✅" if code == 200 else ("⚠️" if code in (401, 403, 302, 404) else "❌")
    log(f"  {mark} [{status_text}] {method} {path} -> {resp_body[:120]!r}")

# 3) 探测 Cookie/认证要求
log("")
log("=== 未认证访问响应头 ===")
path = "/console/api/apps"
h = {"User-Agent": "Mozilla/5.0"}
req = urllib.request.Request(TARGET + path, headers=h)
try:
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    log(f"  200 OK - Set-Cookie: {resp.headers.get('Set-Cookie', '无')}")
except urllib.error.HTTPError as e:
    log(f"  {e.code} - WWW-Authenticate: {e.headers.get('WWW-Authenticate', '无')}")
    log(f"  Set-Cookie: {e.headers.get('Set-Cookie', '无')}")
    log(f"  Location: {e.headers.get('Location', '无')}")
except Exception as e:
    log(f"  ERR: {e}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))