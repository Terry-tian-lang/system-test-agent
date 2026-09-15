# -*- coding: utf-8 -*-
"""
================================================================================
 接口自动化回归脚本 (单文件 · PyCharm 直接运行 · 零第三方依赖)
================================================================================
 适用平台: ai-func(魔改Dify 智能体平台) / rag-func(魔改RagFlow 知识库平台) / cas-func(CAS登录)
 运行方式:
   1) 直接用 PyCharm 打开本文件 -> 右键 Run (或 Shift+F10)
   2) 也可命令行:  python interface_auto_test.py [--token X --token-ragflow Y --mode full]
 功能:
   - verify 模式: 无需 Token, 验证接口路由可达性 (建议先跑这个)
   - full  模式: 携带真实 Token, 执行业务回归 (默认 --readonly 只读安全)
   - 自动输出 HTML 报告到 output/ 目录 (无需安装 openpyxl)
   - RagFlow 域自动识别业务 code (code=0 成功 / 102-109 受限 / 100+404 路由缺失)
 修改配置: 直接编辑下面的 CONFIG 字典即可 (Token 只在本地, 注意不要外传)
================================================================================
"""

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

# 控制台输出保护: Windows GBK 终端无法打印 emoji, 重配为 UTF-8 (PyCharm 默认即 UTF-8)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ==============================================================================
# ① 配置区 —— 在此处填入你的 Token / 地址 / 模式 (PyCharm 用户改这里!)
# ==============================================================================
CONFIG = {
    # ---- 三个服务的基础地址 ----
    "dify_base":     "http://ai-func.ibosssoft.com.cn",     # 智能体平台(魔改Dify)
    "ragflow_base":  "http://rag-func.ibosssoft.com.cn",    # 知识库平台(魔改RagFlow)
    "cas_base":      "http://cas-func.ibosssoft.com.cn",    # CAS 单点登录

    # ---- Token / API Key (留空则跳过需要认证的 full 业务回归) ----
    "dify_token":     "",    # Dify Bearer Token (想跑 Dify 业务回归时填入)
    "ragflow_token":  "",    # RagFlow API Key (想跑 RagFlow 业务回归时填入)

    # ---- 运行模式 ----
    "mode":       "verify",  # verify=路由可达性(免Token) | full=业务回归(需Token)
    "readonly":   True,      # full 模式下 True=只读(GET/检索), False=含写操作(真实创建/删除!)
    "timeout":    15,        # 单请求超时(秒)
    "delay":      0.05,      # 请求间隔(秒), 防限流
    "prefix":     "",        # 仅跑某前缀用例, 如 "RAG" 或 "Agent" (空=全部)
    "case":       "",        # 仅跑单条用例, 如 "Agent-012" (空=全部)

    # ---- 内置核心场景开关: True=无外部文件也能跑(内置~30条冒烟), False=仅用全量场景 ----
    "use_builtin": True,
}
# ==============================================================================

# RagFlow 业务 code 语义: 详细判定见 _judge_ragflow
RESULT_STYLE = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "BLOCKED": "🚫", "ERROR": "💥"}

# 上下文占位(用于 full 模式真实 ID 替换)
SAMPLE_UUID = "01234567-89ab-4def-8123-456789abcdef"


# ==============================================================================
# ② 内置核心冒烟场景 (无外部文件时也能独立运行; 全量131条见 api_test/regression_scenarios.py)
#    字段: method/path/base/expect(命中即过)/expect_code/params(请求体)/desc/note
#    路径占位: {id}=应用ID {dataset_id}=知识库ID {document_id}=文档ID {task_id}=任务ID
# ==============================================================================
BUILTIN_SCENARIOS = {
    # ---------------------------- Agent 侧 (ai-func / Dify) ----------------------------
    "Agent-011": {"title": "从模板复制智能体", "module": "应用管理", "priority": "P0", "service": "dify", "steps": [
        {"method": "GET", "path": "/explore/apps", "expect": ["200"], "desc": "模板市场列表"},
        {"method": "POST", "path": "/console/api/apps", "expect": ["200"], "desc": "复制模板创建应用", "skip_write": True},
    ]},
    "Agent-012": {"title": "从0创建智能体(助手)", "module": "应用管理", "priority": "P0", "service": "dify", "steps": [
        {"method": "GET", "path": "/console/api/apps", "expect": ["200"], "desc": "应用列表"},
        {"method": "POST", "path": "/console/api/apps", "expect": ["200"], "params": {"mode": "chat", "name": "回归-断言用"}, "desc": "创建聊天助手", "skip_write": True},
    ]},
    "Agent-014": {"title": "Prompt编辑-模型选择", "module": "编排", "priority": "P0", "service": "dify", "steps": [
        {"method": "GET", "path": "/console/api/workspaces/current/model-providers", "expect": ["200"], "desc": "模型供应商列表"},
    ]},
    "Agent-015": {"title": "智能体-变量", "module": "编排", "priority": "P0", "service": "dify", "steps": [
        {"method": "GET", "path": "/console/api/apps", "expect": ["200"], "desc": "应用列表"},
        {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft", "expect": ["200", "404"], "desc": "草稿详情(魔改版可能404)"},
    ]},
    "Agent-019": {"title": "查看API接入文档", "module": "应用管理", "priority": "P0", "service": "dify", "steps": [
        {"method": "GET", "path": "/console/api/apps/{id}/api-keys", "expect": ["200", "503"], "desc": "API密钥(沙箱计划可能503禁用)"},
    ]},
    "Agent-025": {"title": "导出配置", "module": "应用管理", "priority": "P1", "service": "dify", "steps": [
        {"method": "GET", "path": "/console/api/apps/{id}/export", "expect": ["200"], "desc": "导出DSL配置"},
    ]},
    "Agent-037": {"title": "知识检索-基础配置", "module": "编排", "priority": "P0", "service": "dify", "steps": [
        {"method": "POST", "path": "/console/api/datasets/{dataset_id}/hit-testing", "expect": ["200", "400"], "params": {"query": "测试", "retrieval_model": {"top_k": 5}}, "desc": "知识库命中测试"},
    ]},
    "Agent-053": {"title": "工具节点-插件", "module": "编排", "priority": "P0", "service": "dify", "steps": [
        {"method": "GET", "path": "/console/api/workspaces/current/tool-providers", "expect": ["200"], "desc": "工具供应商列表"},
    ]},
    "Agent-061": {"title": "访问知识库平台-跳转", "module": "集成", "priority": "P0", "service": "dify", "steps": [
        {"method": "GET", "path": "/", "expect": ["200"], "desc": "平台首页可达"},
    ]},
    "Agent-062": {"title": "SSO单点登录", "module": "集成", "priority": "P0", "service": "cas", "steps": [
        {"method": "GET", "path": "/cas", "expect": ["200", "302"], "desc": "CAS入口"},
    ]},
    "Agent-069": {"title": "页面访问智能体", "module": "发布", "priority": "P0", "service": "dify", "steps": [
        {"method": "GET", "path": "/apps", "expect": ["200"], "desc": "前端应用页面"},
    ]},

    # ---------------------------- RAG 侧 (rag-func / RagFlow) ----------------------------
    "RAG-002": {"title": "搜索工作空间", "module": "工作空间", "priority": "P0", "service": "ragflow", "steps": [
        {"method": "GET", "path": "/api/v1/datasets?page=1&page_size=10", "expect": ["200"], "desc": "知识库列表(代理工作空间搜索)"},
    ]},
    "RAG-006": {"title": "查看成员", "module": "工作空间", "priority": "P1", "service": "ragflow", "steps": [
        {"method": "GET", "path": "/api/v1/datasets?page=1&page_size=1", "expect": ["200"], "desc": "工作空间数据可达"},
    ]},
    "RAG-011": {"title": "知识库列表", "module": "知识库", "priority": "P0", "service": "ragflow", "steps": [
        {"method": "GET", "path": "/api/v1/datasets?page=1&page_size=10", "expect": ["200"], "desc": "查看知识库列表"},
    ]},
    "RAG-023": {"title": "查看切片结果", "module": "知识库", "priority": "P0", "service": "ragflow", "steps": [
        {"method": "GET", "path": "/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks", "expect": ["200"], "desc": "切片列表(库中无文档时受限)"},
    ]},
    "RAG-024": {"title": "知识库检索测试", "module": "知识库", "priority": "P0", "service": "ragflow", "steps": [
        {"method": "POST", "path": "/api/v1/searchbots/retrieval_test", "expect": ["200"], "params": {"kb_id": "{dataset_id}", "question": "回归测试", "top_k": 5}, "desc": "检索测试(真实路由, searchbots域)"},
    ]},
    "RAG-028": {"title": "查看文件解析状态", "module": "知识库", "priority": "P0", "service": "ragflow", "steps": [
        {"method": "GET", "path": "/api/v1/datasets/{dataset_id}/documents/status", "expect": ["200"], "desc": "解析状态(真实路由)"},
    ]},
    "RAG-053": {"title": "标签库列表", "module": "标签", "priority": "P0", "service": "ragflow", "steps": [
        {"method": "GET", "path": "/api/v1/tags?tag_base_id={dataset_id}", "expect": ["200"], "desc": "标签列表(真实路由)"},
    ]},
}


# ==============================================================================
# ③ 全量场景自动加载: 同目录或上级 api_test/ 存在 regression_scenarios.py 时使用131条全量
# ==============================================================================
def load_scenarios(use_builtin=True):
    """优先加载全量场景表; 找不到时回退内置冒烟场景. 返回 (scenarios_dict, source_str)"""
    here = os.path.dirname(os.path.abspath(__file__))
    cand = [
        os.path.join(here, "regression_scenarios.py"),
        os.path.join(here, "..", "api_test", "regression_scenarios.py"),
        os.path.join(here, "api_test", "regression_scenarios.py"),
    ]
    for c in cand:
        if os.path.exists(c):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("regression_scenarios", c)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sc = getattr(mod, "SCENARIOS", {})
                if sc:
                    return sc, f"全量场景 {len(sc)} 条 <- {os.path.basename(c)}"
            except Exception as e:
                print(f"[warn] 加载全量场景失败({e}), 使用内置场景")
                break
    if use_builtin:
        return BUILTIN_SCENARIOS, f"内置冒烟场景 {len(BUILTIN_SCENARIOS)} 条 (未找到全量场景表)"
    return {}, "无场景"


# ==============================================================================
# ④ 请求执行器 (纯标准库 urllib, 支持 HTTPS 自签证书)
# ==============================================================================
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


def send_request(method, url, headers, body=None, timeout=15):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX)
        raw = resp.read()
        try:
            text = raw.decode("utf-8")
        except Exception:
            text = raw.decode("gbk", "ignore")
        return resp.status, text
    except urllib.error.HTTPError as e:
        raw = e.read() or b""
        try:
            text = raw.decode("utf-8", "ignore")
        except Exception:
            text = raw.decode("gbk", "ignore")
        return e.code, text
    except Exception as e:
        return -1, str(e)


def build_headers(service, dify_token, ragflow_token):
    h = {"User-Agent": "Mozilla/5.0 (InterfaceAutoTest)", "Accept": "application/json"}
    tok = ragflow_token if service == "ragflow" else dify_token
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def fill_path(path, ctx, service):
    """替换路径占位符为真实ID (full模式预取过) / 样例UUID"""
    out = path
    out = out.replace("{id}", ctx.get("app_id", SAMPLE_UUID))
    out = out.replace("{dataset_id}", ctx.get("rf_dataset_id" if service == "ragflow" else "dataset_id", SAMPLE_UUID))
    out = out.replace("{document_id}", ctx.get("document_id", SAMPLE_UUID))
    out = out.replace("{task_id}", ctx.get("task_id", SAMPLE_UUID))
    out = out.replace("{tag_id}", ctx.get("tag_id", SAMPLE_UUID))
    return out


# ==============================================================================
# ⑤ 判定引擎 (verify / full 双语义 + RagFlow 业务code)
# ==============================================================================
def judge_step(service, status, resp_text, step, mode):
    """返回 (verdict, detail)"""
    expect = step.get("expect") or ["200"]
    expect_code = step.get("expect_code", 200)
    expect_any = step.get("expect_any", [])
    msg = (resp_text or "").strip()[:150].replace("\n", " ")

    if mode == "verify":
        if status == 404 or status == -1:
            return "FAIL", f"路由不存在/网络异常 实得{status}"
        if status in (401, 403) or 200 <= status < 400 or status in (405, 503):
            note = {401: "需认证", 403: "禁止访问", 405: "方法待修正", 503: "功能禁用"}.get(status, "")
            return "PASS", f"实得{status} 路由存在{('('+note+')') if note else ''}"
        return "FAIL", f"意外状态 {status}"

    # ---- full 模式 ----
    # RagFlow 域: HTTP 200 但业务 code 才代表真实结果
    if service == "ragflow" and resp_text:
        try:
            d = json.loads(resp_text)
            if isinstance(d, dict) and isinstance(d.get("code"), (int, str)):
                bc = str(d.get("code"))
                if bc in ("0", "200"):
                    return "PASS", f"业务成功(code={bc})"
                if bc in ("109", "102"):
                    return "BLOCKED", f"路由存在但凭证/资源受限(code={bc}): {msg}"
                if bc == "101":
                    return "BLOCKED", f"路由存在但参数缺失(code=101): {msg}"
                if bc == "100":
                    if "404" in msg:
                        return "FAIL", f"路由不存在(code=100/404): {msg}"
                    if "405" in msg:
                        return "FAIL", f"路由方法错误(code=100/405): {msg}"
                    return "FAIL", f"业务错误(code=100): {msg}"
                return "FAIL", f"业务错误(code={bc}): {msg}"
        except Exception:
            pass

    if status == 503:
        return "BLOCKED", "环境功能禁用(503)"
    if status == 404:
        return "FAIL", f"资源/路由不存在(404) 期望{expect_code}"
    if expect_any and status in expect_any:
        hint = step.get("note_hint", "")
        return "PASS", f"实得{status} {('['+hint+']') if hint else ''}"
    if status == expect_code:
        return "PASS", f"期望{expect_code} 实得{status}"
    if str(status) in expect:
        return "PASS", f"实得{status}(预期列表内)"
    return "FAIL", f"期望{expect_code} 实得{status} {('| '+msg) if msg else ''}"


def is_readonly_step(step):
    """写方法且非检索/测试类 = 写操作 (full 模式 readonly 时跳过)"""
    m = step.get("method", "GET").upper()
    if m == "GET":
        return True
    if m == "POST":
        p = step.get("path", "")
        if any(k in p for k in ("hit-testing", "retrieval-test", "retrieval_test",
                                "use-check", "check-dependencies", "dynamic-options",
                                "latest-versions")):
            return True
        return False
    if step.get("skip_write"):
        return False
    return False


# ==============================================================================
# ⑥ 预取真实资源ID (full 模式; 用 Dify/RagFlow 列表接口获取真实ID替换占位)
# ==============================================================================
def prefetch_ids(cfg):
    ctx = {}
    # Dify 应用
    if cfg["dify_token"]:
        try:
            code, txt = send_request("GET", cfg["dify_base"] + "/console/api/apps",
                                     build_headers("dify", cfg["dify_token"], cfg["ragflow_token"]),
                                     timeout=cfg["timeout"])
            if code == 200:
                d = json.loads(txt)
                data = d.get("data") or []
                for app in data:
                    if app.get("mode") in ("advanced-chat", "workflow", "agent-chat"):
                        ctx["app_id"] = app.get("id", "")
                        break
                if "app_id" not in ctx and data:
                    ctx["app_id"] = data[0].get("id", "")
        except Exception as e:
            print(f"  [warn] Dify 应用预取失败: {e}")
    # Dify 知识库
    if cfg["dify_token"]:
        try:
            code, txt = send_request("GET", cfg["dify_base"] + "/console/api/datasets",
                                     build_headers("dify", cfg["dify_token"], cfg["ragflow_token"]),
                                     timeout=cfg["timeout"])
            if code == 200:
                d = json.loads(txt)
                data = d.get("data") or []
                if data:
                    ctx["dataset_id"] = data[0].get("id", "")
        except Exception:
            pass
    # RagFlow 知识库
    if cfg["ragflow_token"]:
        try:
            code, txt = send_request("GET", cfg["ragflow_base"] + "/api/v1/datasets?page=1&page_size=5",
                                     build_headers("ragflow", cfg["dify_token"], cfg["ragflow_token"]),
                                     timeout=cfg["timeout"])
            if code == 200:
                d = json.loads(txt)
                data = d.get("data") or []
                if data:
                    ctx["rf_dataset_id"] = data[0].get("id", "")
        except Exception:
            pass
    return ctx


# ==============================================================================
# ⑦ 主流程: 执行全部/过滤用例
# ==============================================================================
def run_all(scenarios, cfg, ctx):
    results = []
    items = list(scenarios.items())
    if cfg["prefix"]:
        items = [it for it in items if it[0].startswith(cfg["prefix"])]
    if cfg["case"]:
        items = [it for it in items if it[0] == cfg["case"]]
    for case_id, case in items:
        r = run_case(case_id, case, cfg, ctx)
        results.append(r)
        print(f"  {RESULT_STYLE.get(r['verdict'], '❓')} [{r['verdict']:7s}] {case_id} {case.get('title','')}")
    return results


def run_case(case_id, case, cfg, ctx):
    service = case.get("service", "dify")
    base = case.get("base") or (cfg["ragflow_base"] if service == "ragflow"
                                else cfg["cas_base"] if service == "cas" else cfg["dify_base"])
    steps = case.get("steps", [])
    step_results, executed = [], []

    for s in steps:
        method = s.get("method", "GET")
        path = fill_path(s.get("path", ""), ctx, service)
        url = base.rstrip("/") + path
        # readonly 模式跳过写操作
        if cfg["readonly"] and cfg["mode"] == "full" and not is_readonly_step(s):
            step_results.append({"step": method + " " + path, "verdict": "SKIP",
                                 "detail": "readonly模式跳过写操作", "cost": 0})
            continue
        t0 = time.time()
        try:
            status, text = send_request(method, url,
                                        build_headers(service, cfg["dify_token"], cfg["ragflow_token"]),
                                        body=s.get("params"), timeout=cfg["timeout"])
        except Exception as e:
            status, text = -1, str(e)
        cost = round(time.time() - t0, 2)
        verdict, detail = judge_step(service, status, text, s, cfg["mode"])
        step_results.append({"step": method + " " + path, "verdict": verdict,
                             "detail": detail + (f" ({status})" if status != -1 else ""), "cost": cost})
        if verdict != "SKIP":
            executed.append(verdict)
        if cfg["delay"]:
            time.sleep(cfg["delay"])

    if not executed:
        verdict, detail = "SKIP", "全部步骤被跳过(纯UI/写操作)"
    elif "FAIL" in executed:
        verdict, detail = "FAIL", f"{len(step_results)}步, 失败{executed.count('FAIL')}步"
    elif "BLOCKED" in executed and all(v == "BLOCKED" for v in executed):
        verdict, detail = "BLOCKED", f"{len(step_results)}步, 环境受限{executed.count('BLOCKED')}步"
    elif all(v in ("PASS", "BLOCKED") for v in executed):
        verdict, detail = "PASS", f"{len(step_results)}步, 失败0步 (受限{executed.count('BLOCKED')}步)"
    else:
        verdict, detail = "PASS", f"{len(step_results)}步, 失败0步"

    return {"case_id": case_id, "title": case.get("title", ""), "module": case.get("module", ""),
            "priority": case.get("priority", ""), "service": service, "verdict": verdict,
            "detail": detail, "steps": step_results}


# ==============================================================================
# ⑧ HTML 报告
# ==============================================================================
def gen_html_report(results, cfg, source):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vc = {}
    for r in results:
        vc[r["verdict"]] = vc.get(r["verdict"], 0) + 1
    total = len(results)

    rows = []
    for r in results:
        st = "".join(f"<span class='v {v.lower()}'>{RESULT_STYLE.get(v, '?')} {v}</span>" for v in
                     dict.fromkeys(s["verdict"] for s in r["steps"])) or "—"
        rows.append(
            f"<tr><td>{r['case_id']}</td><td>{r['title']}</td><td>{r['module']}</td>"
            f"<td>{r['priority']}</td><td>{r['service']}</td>"
            f"<td class='v {r['verdict'].lower()}'>{RESULT_STYLE.get(r['verdict'], '?')} {r['verdict']}</td>"
            f"<td>{r['detail']}</td></tr>"
        )

    detail_rows = []
    for r in results:
        for s in r["steps"]:
            if s["verdict"] in ("FAIL", "BLOCKED", "ERROR"):
                detail_rows.append(
                    f"<tr><td>{r['case_id']}</td><td>{r['title']}</td><td>{s['step']}</td>"
                    f"<td class='v {s['verdict'].lower()}'>{RESULT_STYLE.get(s['verdict'], '?')} {s['verdict']}</td>"
                    f"<td>{s['detail']}</td></tr>"
                )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>接口自动化回归报告</title>
<style>
 body{{font-family:"Microsoft YaHei",sans-serif;margin:24px;background:#f7f8fa;color:#222}}
 h1{{font-size:22px}} h2{{font-size:17px;margin-top:28px;border-left:4px solid #2f6fed;padding-left:8px}}
 .meta{{color:#666;font-size:13px;margin:4px 0}}
 table{{border-collapse:collapse;width:100%;background:#fff;font-size:13px;margin-top:8px}}
 th,td{{border:1px solid #e3e6ea;padding:6px 8px;text-align:left}}
 th{{background:#2f6fed;color:#fff}}
 tr:nth-child(even){{background:#fafbfc}}
 .cards{{display:flex;gap:14px;margin:14px 0;flex-wrap:wrap}}
 .card{{background:#fff;border:1px solid #e3e6ea;border-radius:8px;padding:12px 22px;text-align:center;min-width:110px}}
 .card b{{font-size:26px;display:block}} .card small{{color:#888}}
 .v.pass{{color:#1a7f37;font-weight:bold}} .card.pass b{{color:#1a7f37}}
 .v.fail{{color:#cf222e;font-weight:bold}} .card.fail b{{color:#cf222e}}
 .v.blocked{{color:#b07d1f;font-weight:bold}} .card.blocked b{{color:#b07d1f}}
 .v.skip{{color:#888}} .card.skip b{{color:#888}}
 pre{{background:#0d1117;color:#e6edf3;padding:12px;border-radius:6px;overflow:auto}}
</style></head><body>
<h1>🔁 接口自动化回归报告</h1>
<p class="meta">执行时间: {now} &nbsp;|&nbsp; 模式: {cfg['mode']}{'(只读)' if cfg['mode']=='full' and cfg['readonly'] else ''}
 &nbsp;|&nbsp; 场景: {source} &nbsp;|&nbsp; 用例: {total}</p>
<div class="cards">
 <div class="card pass"><b>{vc.get('PASS',0)}</b><small>✅ 通过</small></div>
 <div class="card fail"><b>{vc.get('FAIL',0)}</b><small>❌ 失败</small></div>
 <div class="card blocked"><b>{vc.get('BLOCKED',0)}</b><small>🚫 受限</small></div>
 <div class="card skip"><b>{vc.get('SKIP',0)}</b><small>⏭️ 跳过</small></div>
</div>
<h2>用例结果明细</h2>
<table><tr><th>用例</th><th>标题</th><th>模块</th><th>优先级</th><th>服务</th><th>结果</th><th>详情</th></tr>
{''.join(rows) if rows else '<tr><td colspan=7>无执行用例</td></tr>'}
</table>
<h2>失败 / 受限步骤明细</h2>
<table><tr><th>用例</th><th>标题</th><th>步骤</th><th>结果</th><th>详情</th></tr>
{''.join(detail_rows) if detail_rows else '<tr><td colspan=5>🎉 无失败或受限步骤</td></tr>'}
</table>
<h2>执行命令</h2>
<pre>python interface_auto_test.py --mode {cfg['mode']} --prefix {cfg['prefix'] or 'ALL'}</pre>
</body></html>"""

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "回归报告")
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(out_dir, f"接口自动化报告_{ts}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


# ==============================================================================
# ⑨ CLI 入口
# ==============================================================================
def main():
    ap = argparse.ArgumentParser(description="接口自动化回归(单文件 PyCharm版)")
    ap.add_argument("--mode", choices=["verify", "full"], default=None)
    ap.add_argument("--token", dest="dify_token", default=None, help="Dify Bearer Token")
    ap.add_argument("--token-ragflow", dest="ragflow_token", default=None, help="RagFlow API Key")
    ap.add_argument("--readonly", action="store_true", default=None, help="full模式只读")
    ap.add_argument("--no-readonly", action="store_true", help="允许写操作(full模式)")
    ap.add_argument("--prefix", default=None, help="按前缀过滤, 如 RAG/Agent")
    ap.add_argument("--case", default=None, help="单条用例, 如 Agent-012")
    ap.add_argument("--timeout", type=int, default=None)
    ap.add_argument("--delay", type=float, default=None)
    args = ap.parse_args()

    # 命令行覆盖 CONFIG
    for k in ("mode", "dify_token", "ragflow_token", "prefix", "case", "timeout", "delay"):
        v = getattr(args, k)
        if v not in (None, ""):
            CONFIG[k] = v
    if args.readonly:
        CONFIG["readonly"] = True
    if args.no_readonly:
        CONFIG["readonly"] = False
    mode = CONFIG["mode"]

    scenarios, source = load_scenarios(CONFIG["use_builtin"])
    print("=" * 70)
    print(f" 接口自动化回归  |  模式: {mode}{'(只读)' if mode=='full' and CONFIG['readonly'] else ''}")
    print(f" 场景: {source}")
    print(f" Dify  : {CONFIG['dify_base']}  Token {'已提供' if CONFIG['dify_token'] else '未提供'}")
    print(f" RagFlow: {CONFIG['ragflow_base']}  Key  {'已提供' if CONFIG['ragflow_token'] else '未提供'}")
    print("=" * 70)

    # 预取真实ID (full 模式)
    ctx = {}
    if mode == "full" and (CONFIG["dify_token"] or CONFIG["ragflow_token"]):
        print("[预取] 获取真实资源ID ...")
        ctx = prefetch_ids(CONFIG)
        got = [f"{k}={v[:12]}..." for k, v in ctx.items() if v]
        print(f"  预取: {('; '.join(got)) if got else '未获得(使用样例UUID)'}")

    t0 = time.time()
    results = run_all(scenarios, CONFIG, ctx)
    cost = round(time.time() - t0, 1)

    vc = {}
    for r in results:
        vc[r["verdict"]] = vc.get(r["verdict"], 0) + 1
    print("=" * 70)
    print(f" 统计: 共 {len(results)} 条 | 通过 {vc.get('PASS',0)} | 失败 {vc.get('FAIL',0)}"
          f" | 受限 {vc.get('BLOCKED',0)} | 跳过 {vc.get('SKIP',0)} | 耗时 {cost}s")
    out = gen_html_report(results, CONFIG, source)
    print(f" HTML报告: {out}  (浏览器打开即可查看)")
    return 0 if not vc.get("FAIL") else 1


if __name__ == "__main__":
    sys.exit(main())