#!/usr/bin/env python3
"""验证 ragflow- 前缀 API Key 有效性(只读)
用法: 先设置环境变量 RAGFLOW_KEY, 或直接运行后按提示输入
    set RAGFLOW_KEY=ragflow-xxxx   (Windows)
"""
import json, os, ssl, sys, urllib.request, urllib.error

KEY = os.environ.get("RAGFLOW_KEY", "").strip() or input("请输入RagFlow API Key(ragflow-开头): ").strip()
if not KEY:
    sys.exit("未提供 Key, 退出")
MASK = KEY[:11] + "..." + KEY[-6:]
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def probe(path, method="GET", body=None):
    url = "http://rag-func.ibosssoft.com.cn" + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "User-Agent": "Mozilla/5.0", "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KEY}",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return resp.status, resp.read().decode("utf-8", "ignore")[:600]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")[:300]
    except Exception as e:
        return -1, str(e)[:120]

print(f"被测Key(掩码): {MASK}")
print("=" * 62)
code, body = probe("/api/v1/datasets")
print(f"1) GET /api/v1/datasets -> [{code}]")
try:
    data = json.loads(body)
    if data.get("code") == 0:
        items = data.get("data", [])
        print(f"   有效! 数据集数量: {len(items)}")
        for it in items[:10]:
            print(f"     - {it.get('id','?')} | {it.get('name','?')} | docs={it.get('doc_count','?')} | chunks={it.get('chunk_count','?')}")
    else:
        print(f"   业务拒绝: {body[:300]}")
except Exception:
    print(f"   非JSON: {body[:200]}")

print()
code, body = probe("/api/v1/datasets/tags")
print(f"2) GET /api/v1/datasets/tags -> [{code}] {body[:200]}")
print()
code, body = probe("/api/v1/user/info", body={})
print(f"3) (探) /api/v1/user/info -> [{code}] {body[:200]}")