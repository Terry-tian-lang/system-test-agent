#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库业务 (/dmwh 数据管理模块) 接口扫描工具
用法: python tools/scan_dmwh_interfaces.py [--readonly]
凭据从项目根目录 .env 读取:
  RAG_DMWH_AUTH=<页面Authorization值>
  RAG_DMWH_COOKIE=<页面Cookie值>
产出: output/回归报告/数据库业务_接口清单_<ts>.md + .json
"""
import io, json, os, re, ssl, sys, time, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://rag-func.ibosssoft.com.cn"
PREFIX = "/dmwh"
OUT_DIR = ROOT / "output" / "回归报告"

# ---- 从 .env 加载凭据 ----
def load_env():
    env = {}
    for p in (ROOT / ".env",):
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env

_env = load_env()
AUTH = _env.get("RAG_DMWH_AUTH", "")
COOKIE = _env.get("RAG_DMWH_COOKIE", "")
if not AUTH or not COOKIE:
    print("缺少凭据: 请在项目根目录 .env 中配置 RAG_DMWH_AUTH / RAG_DMWH_COOKIE")
    sys.exit(1)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ---------- 1) 提取 /dmwh 路径模板 ----------
s = (ROOT / "output" / "rag_chunks" / "umi.5f3c50bb.js").read_text(encoding="utf-8", errors="ignore")
raw_tpls = set()
for m in re.finditer(r'concat\(r,"(/[^"]{2,80})"\)', s):
    raw_tpls.add(m.group(1))
for m in re.finditer(r'concat\(r,"(/[^"]{1,60})"\)\.concat\(encodeURIComponent\(String\(([a-z])\)\),"([^"]{1,40})"\)', s):
    raw_tpls.add(m.group(1) + "{" + m.group(2) + "}" + m.group(3))
for m in re.finditer(r'concat\(r,"(/[^"]{1,60})"\)(.*?)(?:,|\))', s):
    p = m.group(1)
    rest = m.group(2)
    if "concat" in rest:
        parts = re.findall(r'concat\([^,]{0,40},?"([^"]{1,50})"\)', rest)
        raw_tpls.add(p + "{param}" + "".join(parts) if parts else p)
    else:
        raw_tpls.add(p)

def clean(p):
    if not p.startswith("/"):
        return False
    if any(ch in p for ch in (" ", "\n", "\t", "'", '"', "{", "}", "\\")):
        return False
    if not re.fullmatch(r"[/\w\-_.{}]+", p):
        return False
    return True

paths = sorted({p for p in raw_tpls if clean(p)})

# ---------- 2) 探测 ----------
def probe(path, method):
    url = BASE + PREFIX + path
    body = b"{}" if method in ("POST", "PUT") else None
    h = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json",
         "Cookie": COOKIE, "Authorization": AUTH}
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        resp = urllib.request.urlopen(req, timeout=12, context=ctx)
        return resp.status, resp.read().decode("utf-8", "ignore")[:260]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")[:180]
    except Exception as e:
        return -1, str(e)[:90]

METHODS = ["GET", "POST", "PUT", "DELETE"]

def classify(status, body):
    b = body.strip()
    if status == 200:
        try:
            d = json.loads(b)
            code = str(d.get("code"))
            if code in ("0", "200"):
                return "OK", (d.get("message") or "成功")[:44]
            return f"BIZ{code}", (d.get("message") or "")[:44]
        except Exception:
            return "OK", "200 非JSON"
    if status in (401, 403):
        return "AUTH", ""
    if status == 405:
        return "M401", ""
    if status == 404:
        return "NF", ""
    if status in (400, 422):
        return "OK400", b[:44]
    if status in (500, 502):
        return "ERR500", b[:44]
    return f"HT{status}", b[:44]

results = {}
for p in paths:
    row = {}
    for m in METHODS:
        st, body = probe(p, m)
        v, msg = classify(st, body)
        row[m] = (st, v, msg)
        time.sleep(0.02)
    results[p] = row
    time.sleep(0.01)

# ---------- 3) 分组排序 ----------
MODULES = ["data_source", "data_model", "data_subject", "data_mapping", "data_integration",
           "trans_plan", "task_manager", "common"]
def mod_key(p):
    m = p.split("/")[1]
    return MODULES.index(m) if m in MODULES else len(MODULES)

def pick(row):
    order = {"OK": 0, "OK400": 0, "ERR500": 2, "AUTH": 3, "M401": 4, "HT": 5, "NF": 6}
    best = None
    for m, (st, v, msg) in row.items():
        tag = v.split("0")[0] if v.startswith("BIZ") else v
        sc = order.get(tag, 7)
        if best is None or sc < best[0] or (sc == best[0] and tag == "OK"):
            best = (sc, m, st, v, msg)
    return best[1:]

# ---------- 4) 报告 ----------
md = []
md.append("# 数据库业务（数据管理 /dmwh）接口清单\n")
md.append(f"- 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
md.append(f"- 目标: `{BASE}{PREFIX}`")
md.append(f"- 认证: 页面会话 (Authorization + session Cookie)")
md.append(f"- 说明: `{{param}}`/`{{e}}` 为真实ID占位; 判定取各方法最优结果\n")

cur = None
for p in sorted(paths, key=lambda x: (mod_key(x), x)):
    m = p.split("/")[1]
    if m != cur:
        cur = m
        md.append(f"\n## {m}\n")
        md.append("| 接口路径 | 方法 | 判定 | 响应 |")
        md.append("|---|---|---|---|")
    row = results[p]
    meth, st, v, msg = pick(row)
    f = []
    for mm in METHODS:
        s2, v2, _ = row[mm]
        if v2 != "NF":
            f.append(f"{mm}->{s2}")
    md.append(f"| `{p}` | **{meth}** | {v} | {('; '.join(f))} |")

ok = sum(1 for r in results.values() if pick(r)[2] in ("OK", "OK400"))
nf = sum(1 for r in results.values() if pick(r)[2] == "NF")
rest = len(results) - ok - nf
md.append(f"\n## 统计: 接口总数 {len(results)} | 可用 {ok} | 受限/异常 {rest} | 不存在 {nf}")
md.append("\n> ⚠️ 安全提示: 探测为只读语义; `DELETE/PUT` 为真实写接口, 请勿在生产环境随意触发。")

OUT_DIR.mkdir(parents=True, exist_ok=True)
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
out = OUT_DIR / f"数据库业务_接口清单_{ts}.md"
out.write_text("\n".join(md), encoding="utf-8")

jlist = []
for p in sorted(paths, key=lambda x: (mod_key(x), x)):
    meth, st, v, msg = pick(results[p])
    jlist.append({"path": p, "module": p.split("/")[1], "best_method": meth,
                  "verdict": v, "status": st, "methods": {k: results[p][k][:2] for k in METHODS}})
json_out = {"base": BASE + PREFIX, "auth": "session", "scanned_at": ts, "total": len(jlist), "items": jlist}
(OUT_DIR / f"数据库业务_接口清单_{ts}.json").write_text(json.dumps(json_out, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"报告: {out}")
print(f"统计: 总数{len(results)} 可用{ok} 受限{rest} 不存在{nf}")
for p in sorted(paths, key=lambda x: (mod_key(x), x)):
    meth, st, v, msg = pick(results[p])
    print(f"  {v:8s} [{meth:6s}] {p}")