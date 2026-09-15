#!/usr/bin/env python3
"""提取完整接口清单：重点抓 运行/聊天/应用 相关端点"""
import sys, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "output" / "api_inventory_raw.txt"
lines = []
def log(m=""):
    lines.append(m)

js_dir = ROOT / "output" / "js_chunks"
ALL = ""
for f in sorted(js_dir.glob("*.js")):
    ALL += f.read_text(encoding="utf-8", errors="ignore") + "\n"

# 1) 所有字符串字面量 API 路径(带模板变量, 保留)
paths = set()
for m in re.finditer(r'["\'`](/(?:console/api|v1|explore|chat|apps|datasets|files|workspaces|account|tools|workflow|spaces|features|setup)[a-zA-Z0-9_\-/\.${}]*?)["\'`]', ALL):
    p = m.group(1)
    paths.add(p)

log(f"=== 字面量路径 ({len(paths)}) ===")
for p in sorted(paths):
    log(f"  {p}")

# 2) 含消息/会话/聊天语义的调用(运行时 API)
log("")
log("=== 运行时/聊天相关调用 ===")
frags = set()
for pat in [r'["\'`]([^"\'`]*(?:chat-messages|conversations|messages|completion|stop|audio|suggested|parameter|debug)[^"\'`]*)["\'`]']:
    for m in re.finditer(pat, ALL):
        v = m.group(1)
        if v.startswith("/") or "/" in v[:3]:
            frags.add(v)
for f in sorted(frags)[:80]:
    log(f"  {f}")

# 3) HTTP 方法+路径 组合调用
log("")
log("=== method+path 组合 (post/get/put/del/patch 调用) ===")
calls = set()
for m in re.finditer(r'(?:post|get|put|delete|patch|del)\s*\(\s*["\'`]([^"\'`]+)["\'`]', ALL, re.I):
    calls.add(m.group(1))
for c in sorted(calls)[:100]:
    log(f"  {c}")

# 4) 认证/会话相关
log("")
log("=== 认证/会话端点 ===")
auth = set()
for m in re.finditer(r'["\'`]([^"\'`]*(?:session|login|logout|token|sign-in|sign-in-api|passport|oauth|sso|refresh)[^"\'`]*)["\'`]', ALL):
    v = m.group(1)
    if v.startswith("/") and len(v) < 100:
        auth.add(v)
for a in sorted(auth)[:50]:
    log(f"  {a}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"完成: {len(paths)} 路径, 详见 {OUT}")