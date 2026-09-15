#!/usr/bin/env python3
"""验证 sk- 开头的 Key 归属与权限 (只读探测 rag-func / ai-func)
用法: 先设置环境变量 RAG_TOKEN, 或直接运行后按提示输入
"""
import json, os, ssl, sys, urllib.request, urllib.error

KEY = os.environ.get("RAG_TOKEN", "").strip() or input("请输入 sk- 开头的 Token: ").strip()
if not KEY:
    sys.exit("未提供 Token, 退出")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def probe(base, path, method="GET"):
    url = base + path
    req = urllib.request.Request(url, method=method, headers={
        "User-Agent": "Mozilla/5.0", "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KEY}",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=12, context=ctx)
        return resp.status, resp.read().decode("utf-8", "ignore")[:500]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")[:300]
    except Exception as e:
        return -1, str(e)[:120]

print("=== 1) rag-func (RagFlow) ===")
for path in ["/api/v1/datasets", "/api/v1/datasets/tags", "/api/v1/user/login"]:
    code, body = probe("http://rag-func.ibosssoft.com.cn", path)
    print(f"[{code}] {path}")
    print(f"      {body[:220]}")
    print()

print("=== 2) ai-func (Dify) ===")
code, body = probe("http://ai-func.ibosssoft.com.cn", "/console/api/apps")
print(f"[{code}] /console/api/apps")
print(f"      {body[:220]}")

print()
print("=== 3) 尝试解析 ragflow datasets 详情 ===")
code, body = probe("http://rag-func.ibosssoft.com.cn", "/api/v1/datasets")
try:
    data = json.loads(body)
    if isinstance(data, dict) and data.get("code") == 0:
        items = data.get("data", [])
        print(f"  有效！数据集数量: {len(items)}")
        for it in items[:8]:
            print(f"    - {it.get('id','?')} | {it.get('name','?')} | docs={it.get('doc_count','?')} | chunks={it.get('chunk_count','?')}")
    else:
        print(f"  业务响应: {body[:300]}")
except Exception:
    print("  非JSON:", body[:200])