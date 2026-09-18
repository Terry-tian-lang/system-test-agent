#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""收集 6 个 404 伪路径的证据: 生产原始响应 + 前端JS引用片段 (凭据从.env读取)"""
import io, json, os, re, ssl, sys, urllib.request, urllib.error
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\测试专用-deepseek\system-test-agent")

# 从 .env 读取生产凭据
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
BASE = env["PROD_DMWH_BASE"]
AUTH = env["PROD_DMWH_AUTH"]
COOKIE = env["PROD_DMWH_COOKIE"]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

PATHS = [
    ("SJZL-014", "/data_model/model_folder_type/all", "模型文件夹类型列表"),
    ("SJZL-016", "/data_source", "数据源根路径"),
    ("SJZL-017", "/data_source/source", "数据源详情路径"),
    ("SJZL-024", "/data_source/storage_types", "存储类型列表"),
    ("SJZL-028", "/data_subject", "数据主题根路径"),
    ("SJZL-039", "/trans_plan/join/generate_create_sql", "联表查询生成SQL"),
]

# 前端 JS 引用片段
js = (ROOT / "output" / "rag_chunks" / "umi.5f3c50bb.js").read_text(encoding="utf-8", errors="ignore")

print("=" * 80)
for cid, path, desc in PATHS:
    print(f"\n### {cid} {desc}  ->  {path}")
    # 1) 生产响应 (注意: API 完整路径 = base + /dmwh 前缀 + path)
    url = BASE + "/dmwh" + path
    h = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json",
         "Cookie": COOKIE, "Authorization": AUTH}
    req = urllib.request.Request(url, method="GET", headers=h)
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        code = resp.status
        body = resp.read().decode("utf-8", "ignore")
        headers = dict(resp.headers)
    except urllib.error.HTTPError as e:
        code = e.code
        body = e.read().decode("utf-8", "ignore")
        headers = dict(e.headers)
    print(f"  生产响应: HTTP {code}")
    print(f"  响应体: {body[:200]}")
    print(f"  响应头Server: {headers.get('Server','?')} | Content-Type: {headers.get('Content-Type','?')}")
    # 2) 前端 JS 引用
    m = re.search(re.escape(path) + r'[^",)]{0,60}', js)
    around = js[max(0, m.start() - 120):m.end() + 60] if m else "未找到"
    print(f"  前端JS引用: ...{around[:220]}...")