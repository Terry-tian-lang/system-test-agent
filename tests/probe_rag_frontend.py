#!/usr/bin/env python3
"""拉取 rag-func 子域的 env.js / umi.js，提取真实 API 配置与路径"""
import sys, re, ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

RAG = "http://rag-func.ibosssoft.com.cn"
OUT_DIR = ROOT / "output" / "rag_chunks"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = ROOT / "output" / "rag_findings.txt"
lines = []
def log(m=""):
    lines.append(m)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(path):
    url = RAG + path
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return resp.status, resp.read().decode("utf-8", "ignore")
    except Exception as e:
        return -1, str(e)[:100]

# 1) env.js — 环境配置
log("=== 1) /env.js 内容 ===")
code, body = fetch("/env.js")
log(f"[{code}] 长度 {len(body)}")
env_path = OUT_DIR / "env.js"
env_path.write_text(body, encoding="utf-8")
log(body[:2000])

# 2) umi 主 JS
log("")
log("=== 2) umi.5f3c50bb.js — 提取 API 路径 ===")
code, body = fetch("/umi.5f3c50bb.js")
log(f"[{code}] 长度 {len(body)}")
umi_path = OUT_DIR / "umi.5f3c50bb.js"
umi_path.write_text(body, encoding="utf-8")

# 3) liteofd.js
code, body2 = fetch("/liteofd.js")
log(f"\n=== 3) liteofd.js [{code}] 长度 {len(body2)}")
(lite_path := OUT_DIR / "liteofd.js").write_text(body2, encoding="utf-8")

# 4) 从 umi.js 提取 API 基础 URL 与路径
log("\n=== 4) umi.js 中的 API 线索 ===")
# 找 base url / 域名
for m in re.finditer(r'https?://[a-zA-Z0-9\.\-]+(?:/[a-zA-Z0-9\-/]*)?', body):
    u = m.group(0)
    if any(k in u for k in ("ibosssoft", "rag", "api")):
        log(f"  域名: {u}")

# 找 fetch/axios 调用路径
paths = set()
for m in re.finditer(r'["\'`]((?:/[a-zA-Z0-9_\-]+){2,}(?:/[a-zA-Z0-9_\-\$\{\}.]+)*)["\'`]', body):
    p = m.group(1)
    if len(p) > 10 and ("pipeline" in p or "workflow" in p or "api" in p or "rag" in p
                        or "dataset" in p or "document" in p or "chat" in p or "stream" in p):
        paths.add(p)
log(f"\n  候选路径 ({len(paths)}):")
for p in sorted(paths)[:60]:
    log(f"    {p}")

# 找 webpack chunk 列表
log("\n=== 5) umi.js 引用的异步 chunk ===")
chunks = set()
for m in re.finditer(r'["\']([a-f0-9]{8}\.async\.js)["\']', body):
    chunks.add(m.group(1))
log(f"  async chunks: {len(chunks)}")
chunk_list = OUT_DIR / "chunk_list.txt"
chunk_list.write_text("\n".join(sorted(chunks)), encoding="utf-8")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))