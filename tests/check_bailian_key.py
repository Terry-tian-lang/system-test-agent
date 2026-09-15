#!/usr/bin/env python3
"""验证 sk-sp- 前缀 Key 的归属: RagFlow接口域 vs 百炼LLM端点 (全程掩码展示)
用法: 先设置环境变量 BAILIAN_KEY, 或直接运行后按提示输入
    set BAILIAN_KEY=sk-sp-xxxx   (Windows)
    export BAILIAN_KEY=sk-sp-xxxx (Linux/Mac)
"""
import json, os, ssl, sys, urllib.request, urllib.error

KEY = os.environ.get("BAILIAN_KEY", "").strip() or input("请输入百炼TokenPlan Key(sk-sp-开头): ").strip()
if not KEY:
    sys.exit("未提供 Key, 退出")
MASK = KEY[:10] + "..." + KEY[-8:]
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def probe(url, headers, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return resp.status, resp.read().decode("utf-8", "ignore")[:400]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")[:300]
    except Exception as e:
        return -1, str(e)[:120]

print(f"被测Key(掩码): {MASK}")
print(f"Key前缀特征: sk-sp-  (百炼TokenPlan专属前缀)")
print("=" * 62)

print("1) rag-func (RagFlow 系统接口域)")
code, body = probe("http://rag-func.ibosssoft.com.cn/api/v1/datasets", {
    "Authorization": f"Bearer {KEY}", "Accept": "application/json"})
print(f"   [{code}] GET /api/v1/datasets -> {body[:160]}")
print()

print("2) ai-func (Dify 系统接口域)")
code, body = probe("http://ai-func.ibosssoft.com.cn/console/api/apps", {
    "Authorization": f"Bearer {KEY}", "Accept": "application/json"})
print(f"   [{code}] GET /console/api/apps -> {body[:160]}")
print()

print("3) 百炼 TokenPlan 兼容端点 (LLM 模型列表)")
code, body = probe("https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/models", {
    "Authorization": f"Bearer {KEY}", "Accept": "application/json"})
print(f"   [{code}] GET /compatible-mode/v1/models -> {body[:300]}")
print()

print("4) 百炼 TokenPlan chat 简单调用 (qwen3.8-max)")
code, body = probe("https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions", {
    "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Accept": "application/json"},
    method="POST",
    body={"model": "qwen3.8-max", "messages": [{"role": "user", "content": "hi"}],
          "max_tokens": 8, "temperature": 0.3})
print(f"   [{code}] -> {body[:300]}")