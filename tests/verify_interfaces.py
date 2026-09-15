#!/usr/bin/env python3
"""
接口真实性验证 - 逐个探测 100 个接口端点

判定规则:
  401 → 端点存在，需认证 (✅ VALID)
  405 → 端点存在，但方法不对 (⚠️ METHOD) - 反推正确方法
  503 → 端点存在，功能被禁用 (⚠️ DISABLED)
  404 → 端点不存在 (❌ INVALID)
  200/3xx → 端点存在且有响应 (✅ OPEN)

注意: 探测使用未认证请求，不涉及业务数据，仅验证路由是否存在。
"""
import sys, time, ssl, json, uuid, re
import urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TARGET = "http://ai-func.ibosssoft.com.cn"
YAML = ROOT / "api_test" / "interfaces" / "ai_func_dify_api.yaml"
OUT = ROOT / "output" / "api_verify_report.txt"
OUT_JSON = ROOT / "output" / "api_verify_result.json"
EXCEL = ROOT / "output" / "接口验证报告.xlsx"

lines = []
def log(m=""):
    lines.append(m)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 样例 ID: UUID 格式，便于路由匹配
SAMPLE_ID = "01234567-89ab-4def-8123-456789abcdef"
SAMPLE_KEY = "sk-test-1234567890"

def fill_params(path: str) -> str:
    """把路径中的 {param} 替换为样例值"""
    out = path
    out = out.replace("{id}", SAMPLE_ID).replace("{doc_id}", SAMPLE_ID)
    out = out.replace("{dataset_id}", SAMPLE_ID).replace("{batch_id}", SAMPLE_ID)
    out = out.replace("{task_id}", SAMPLE_ID).replace("{provider}", "openai")
    out = out.replace("{model_type}", "text-generation")
    out = out.replace("{key_id}", SAMPLE_KEY)
    # 剩余未知参数用 UUID
    out = re.sub(r"\{[a-zA-Z_]+\}", SAMPLE_ID, out)
    return out

import re

def probe(path: str, method: str) -> tuple:
    """发送探测请求，返回 (status_code, body简明)"""
    url = TARGET + fill_params(path)
    if method == "GET" and "?" not in url:
        pass
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Authorization": "Bearer invalid-token-for-probe",
    }, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=12, context=ctx)
        body = resp.read().decode("utf-8", "ignore")[:120]
        return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:120]
        return e.code, body
    except Exception as e:
        return -1, str(e)[:100]

# 加载接口清单
import yaml
data = yaml.safe_load(YAML.read_text(encoding="utf-8"))
interfaces = []
for group, items in data.items():
    if group == "system" or not isinstance(items, list):
        continue
    for item in items:
        if isinstance(item, dict) and "path" in item:
            interfaces.append({
                "path": item["path"],
                "methods": item.get("methods", "try"),
                "group": group,
            })

log(f"待验证接口数: {len(interfaces)}")
log(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
log("")

# 每个接口: 探测列表中的每个方法，若 try 则探测常见方法组合
results = []
stats = {"VALID": 0, "INVALID": 0, "METHOD": 0, "DISABLED": 0, "OPEN": 0, "ERR": 0}

for i, iface in enumerate(interfaces, 1):
    path = iface["path"]
    methods_str = iface["methods"]
    if methods_str == "try":
        method_list = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    else:
        method_list = [m.strip() for m in methods_str.split(",")]

    findings = []   # (method, status, hint)
    for method in method_list:
        code, body = probe(path, method)
        findings.append((method, code, body))
        time.sleep(0.15)  # 礼貌限速

    # 判定
    codes = [f[1] for f in findings]
    if 401 in codes or 403 in codes:
        verdict = "VALID"      # 需认证 → 路由存在
    elif 405 in codes:
        verdict = "METHOD"     # 方法不对但路由存在
    elif 503 in codes:
        verdict = "DISABLED"
    elif 404 in codes and all(c == 404 for c in codes):
        verdict = "INVALID"    # 全404 → 路由不存在
    elif any(200 <= c < 400 for c in codes):
        verdict = "OPEN"
    else:
        verdict = "ERR"

    stats[verdict] = stats.get(verdict, 0) + 1

    # 记录
    detail = "; ".join(f"{m}:{c}" for m, c, _ in findings)
    hint = ""
    for m, c, b in findings:
        if c == 405:
            allow = ""
            hint = f"→ 正确方法可能是非{m}"
            break
        if c == 401 or c == 403:
            hint = "→ 需认证，路由存在"
            break
        if c in (200, 301, 302, 308):
            hint = f"→ 可访问: {b[:60]}"
            break

    results.append({
        "group": iface["group"],
        "path": path,
        "declared_methods": methods_str,
        "probed": detail,
        "verdict": verdict,
        "hint": hint,
    })
    mark = {"VALID": "✅", "INVALID": "❌", "METHOD": "⚠️",
            "DISABLED": "🚫", "OPEN": "🟢", "ERR": "❓"}[verdict]
    log(f"{mark} [{verdict:8s}] {path}  ({detail}) {hint}")
    if i % 10 == 0:
        log(f"--- 进度 {i}/{len(interfaces)} ---")

log("")
log("=" * 70)
log("汇总")
log("=" * 70)
log(f"  存在且需认证 (VALID):    {stats.get('VALID', 0)}")
log(f"  存在但方法待修正 (METHOD): {stats.get('METHOD', 0)}")
log(f"  存在但被禁用 (DISABLED): {stats.get('DISABLED', 0)}")
log(f"  存在可访问 (OPEN):       {stats.get('OPEN', 0)}")
log(f"  不存在 (INVALID):        {stats.get('INVALID', 0)}")
log(f"  网络/异常 (ERR):         {stats.get('ERR', 0)}")
log(f"  合计: {len(interfaces)}")
log("")

# 无效接口列表
invalid = [r for r in results if r["verdict"] == "INVALID"]
if invalid:
    log("=== ❌ 不存在的接口 (需从清单移除) ===")
    for r in invalid:
        log(f"  [{r['group']}] {r['path']}")
log("")

# 方法修正提示
method_fix = [r for r in results if r["verdict"] == "METHOD"]
if method_fix:
    log("=== ⚠️ 方法待修正的接口 ===")
    for r in method_fix:
        log(f"  [{r['group']}] {r['path']}  probed: {r['probed']}")
log("")

# 保存
report_text = "\n".join(lines)
OUT.write_text(report_text, encoding="utf-8")
OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"报告: {OUT}")
print(f"JSON: {OUT_JSON}")
print(report_text)