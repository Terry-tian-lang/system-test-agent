#!/usr/bin/env python3
"""深挖 JS：追踪 base URL 变量定义，提取所有 API 端点"""
import sys, re, ssl, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TARGET = "http://ai-func.ibosssoft.com.cn"
OUT = ROOT / "output" / "probe_js_deep.txt"
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

html = (ROOT / "output" / "system_home.html").read_text(encoding="utf-8", errors="ignore")
js_paths = re.findall(r'src=["\'](/_next/static/[^"\']+\.js)["\']', html)
js_paths = list(dict.fromkeys(js_paths))

# 下载全部 chunk 到本地
js_dir = ROOT / "output" / "js_chunks"
js_dir.mkdir(exist_ok=True)
local_files = []
for js in js_paths:
    name = js.split("/")[-1]
    local = js_dir / name
    if not local.exists():
        try:
            code = fetch(TARGET + js)
            local.write_text(code, encoding="utf-8")
        except Exception:
            continue
    local_files.append(local)
log(f"已缓存 {len(local_files)} 个 JS chunk")

ALL = ""
for f in local_files:
    ALL += f.read_text(encoding="utf-8", errors="ignore") + "\n"

# 1) 追踪 base URL 变量: hy= / hy: 的定义
log("")
log("=== base URL 常量定义 ===")
for pat in [r'hy\s*[:=]\s*["\']([^"\']+)["\']',
            r'baseUrl\s*[:=]\s*["\']([^"\']+)["\']',
            r'apiBase\s*[:=]\s*["\']([^"\']+)["\']',
            r'BASE_URL\s*[:=]\s*["\']([^"\']+)["\']']:
    for m in re.finditer(pat, ALL):
        log(f"  {pat.split(chr(92))[0]}: {m.group(1)}")

# 2) 提取 API 路径字面量（常见的 /xxx/yyy 形式）
log("")
log("=== 候选 API 路径 (正斜杠形式, 去重) ===")
paths = set()
for m in re.finditer(r'["\'`](/(?:api|console|v1|explore|apps|chat|space|files|datasets|features|account|workspace|tools|workflow)[a-zA-Z0-9_\-/{}$\.]*?)["\'`]', ALL):
    p = m.group(1)
    # 只保留纯字面量路径(无模板变量过多)
    if '{' in p and p.count('{') > 2:
        continue
    paths.add(p)
for p in sorted(paths):
    log(f"  {p}")

# 3) fetch/axios 动态拼接模式
log("")
log("=== 动态拼接调用示例 (含 r.hy 或 baseUrl) ===")
seen_call = set()
for m in re.finditer(r'(?:hy|baseUrl)[^;]{0,120}?["\'`]/([a-zA-Z0-9_\-/\.]+)["\'`]', ALL):
    call = m.group(0)[:160]
    if call not in seen_call:
        seen_call.add(call)
        log(f"  {call}")

# 4) 找含 /console/api 或 /v1/ 的完整调用片段
log("")
log("=== /console/api 与 /v1/ 调用片段 ===")
frag = set()
for m in re.finditer(r'(fetch|axios|request|get|post|put|delete|patch)\(["\'`][^"\'`]{0,100}?(/console/api|/v1/|/explore/|/chat/)[^"\'`]{0,120}["\'`]', ALL):
    frag.add(m.group(0)[:180])
for f in sorted(frag)[:40]:
    log(f"  {f}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"分析完成: {len(paths)} 个路径候选, 详见 {OUT}")