#!/usr/bin/env python3
"""
生成 ai-func.ibosssoft.com.cn 接口清单 (v2)
修复: 统一 /console/api 前缀 + Dify 官方方法映射 + 魔改特有 RAG 接口
"""
import sys, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

js_dir = ROOT / "output" / "js_chunks"
ALL = ""
for f in sorted(js_dir.glob("*.js")):
    ALL += f.read_text(encoding="utf-8", errors="ignore") + "\n"

# ---------- 1. 提取前端 JS 中的路径 ----------
paths = set()
for m in re.finditer(r'["\'`]/((?:console/api|v1|datasets|apps|files|workspaces|explore|messages|saved-messages|rag|tools|features)[a-zA-Z0-9_\-/\.${}]*)["\'`]', ALL):
    p = "/" + m.group(1)
    if len(p) > 8:
        paths.add(p)

# ---------- 2. 归一化模板变量 ----------
def norm(p):
    p = p.replace("${t}", "{id}").replace("${s}", "{id}").replace("${r}", "{id}")
    p = p.replace("${e.id}", "{id}").replace("${e}", "{id}")
    p = p.replace("${t.provider}", "{provider}").replace("${r.provider}", "{provider}")
    p = p.replace("${u.zS.textGeneration}", "{model_type}")
    p = re.sub(r'\$\{[^}]+\}', '{param}', p)
    return p

# 补上前缀: JS 中的 /datasets → /console/api/datasets (魔改 Dify console API)
def add_prefix(p):
    if p.startswith("/console/api"):
        return p
    if p.startswith(("/datasets", "/apps", "/files", "/workspaces", "/explore",
                     "/messages", "/saved-messages", "/features", "/tools")):
        return "/console/api" + p
    return p

endpoints = {}
for p in paths:
    p = norm(p)
    p = add_prefix(p)
    # 去掉尾部斜杠
    p = p.rstrip("/")
    key = p
    endpoints[key] = None

# ---------- 3. Dify 官方 console API 方法映射 (依据 Dify v1.x 源码) ----------
METHOD_MAP = {
    # === 应用管理 ===
    "/console/api/apps": "GET,POST",
    "/console/api/apps/{id}": "GET,PATCH,DELETE",
    "/console/api/apps/{id}/copy": "POST",
    "/console/api/apps/{id}/export": "GET",
    "/console/api/apps/{id}/import": "POST",
    "/console/api/apps/{id}/import/confirm": "POST",
    "/console/api/apps/{id}/api-keys": "GET,POST",
    "/console/api/apps/{id}/api-keys/{key_id}": "DELETE",
    "/console/api/apps/{id}/name-generate": "POST",
    "/console/api/apps/{id}/site": "POST",
    "/console/api/apps/{id}/site/access-token/reset": "POST",
    "/console/api/apps/{id}/default-model": "GET,POST",
    "/console/api/apps/{id}/workflows/draft": "GET,POST",
    "/console/api/apps/{id}/workflows/publish": "POST",
    "/console/api/apps/{id}/workflows/run": "POST",
    "/console/api/apps/{id}/workflows/task/{task_id}": "GET",
    "/console/api/apps/{id}/workflows/draft/run": "POST",
    "/console/api/apps/{id}/basic-or-chatbot-mode": "GET",
    "/console/api/apps/{id}/server": "GET,POST",
    # === 数据集管理 ===
    "/console/api/datasets": "GET,POST",
    "/console/api/datasets/{id}": "GET,PATCH,DELETE",
    "/console/api/datasets/{id}/use-check": "GET",
    "/console/api/datasets/{id}/documents": "GET,POST",
    "/console/api/datasets/{id}/documents/{doc_id}": "GET,PATCH,DELETE",
    "/console/api/datasets/{id}/documents/{doc_id}/indexing-status": "GET",
    "/console/api/datasets/{id}/documents/{doc_id}/processing/pause": "POST",
    "/console/api/datasets/{id}/documents/{doc_id}/processing/resume": "POST",
    "/console/api/datasets/{id}/documents/{doc_id}/rename": "POST",
    "/console/api/datasets/{id}/documents/{doc_id}/error-docs": "GET",
    "/console/api/datasets/{id}/documents/{doc_id}/pipeline-execution-log": "GET",
    "/console/api/datasets/{id}/batch/{batch_id}/indexing-status": "GET",
    "/console/api/datasets/{id}/hit-testing": "POST",
    "/console/api/datasets/{id}/external-hit-testing": "POST",
    "/console/api/datasets/{id}/queries": "GET",
    "/console/api/datasets/{id}/retry": "POST",
    "/console/api/datasets/create": "POST",
    "/console/api/datasets/indexing-estimate": "POST",
    "/console/api/datasets/process-rule": "GET",
    "/console/api/datasets/retrieval-setting": "GET",
    "/console/api/datasets/external": "POST",
    "/console/api/datasets/external-knowledge-api": "GET,POST",
    "/console/api/datasets/external-knowledge-api/{id}": "GET,PATCH,DELETE",
    "/console/api/datasets/external-knowledge-api/{id}/use-check": "GET",
    # === 工作区/成员 ===
    "/console/api/workspaces": "GET",
    "/console/api/workspaces/current": "GET,PATCH",
    "/console/api/workspaces/switch": "POST",
    "/console/api/workspaces/current/members": "GET,POST",
    "/console/api/workspaces/current/members/{id}/owner-transfer": "POST",
    "/console/api/workspaces/current/members/owner-transfer-check": "POST",
    "/console/api/workspaces/current/members/send-owner-transfer-confirm-email": "POST",
    # === 模型提供商 ===
    "/console/api/workspaces/current/model-providers": "GET",
    "/console/api/workspaces/current/model-providers/{provider}/credentials": "PUT,PATCH",
    "/console/api/workspaces/current/model-providers/{provider}/credentials/switch": "PATCH",
    "/console/api/workspaces/current/model-providers/{provider}/models": "GET,POST",
    "/console/api/workspaces/current/model-providers/{provider}/models/enable": "PATCH",
    "/console/api/workspaces/current/model-providers/{provider}/models/disable": "PATCH",
    "/console/api/workspaces/current/model-providers/{provider}/preferred-provider-type": "POST",
    "/console/api/workspaces/current/models/model-types/{model_type}": "GET",
    # === 插件 ===
    "/console/api/workspaces/current/plugin/debugging-key": "POST",
    "/console/api/workspaces/current/plugin/install/github": "POST",
    "/console/api/workspaces/current/plugin/install/marketplace": "POST",
    "/console/api/workspaces/current/plugin/install/pkg": "POST,PATCH",
    "/console/api/workspaces/current/plugin/uninstall": "POST",
    "/console/api/workspaces/current/plugin/upgrade/github": "POST",
    "/console/api/workspaces/current/plugin/upgrade/marketplace": "POST",
    "/console/api/workspaces/current/plugin/upload/github": "POST",
    "/console/api/workspaces/current/plugin/tasks/{id}": "GET",
    "/console/api/workspaces/current/plugin/tasks/delete_all": "POST",
    # === 工具/MCP ===
    "/console/api/workspaces/current/tool-providers": "GET",
    "/console/api/workspaces/current/tool-provider/builtin/{provider}/tools": "GET",
    "/console/api/workspaces/current/tool-provider/mcp": "GET,POST",
    "/console/api/workspaces/current/tool-provider/mcp/auth": "POST",
    "/console/api/workspaces/current/tool-provider/mcp/tools/{id}": "GET",
    "/console/api/workspaces/current/tool-provider/mcp/update/{id}": "PATCH",
    "/console/api/workspaces/current/tools/api": "GET,POST",
    "/console/api/workspaces/current/tools/builtin": "GET",
    "/console/api/workspaces/current/tools/mcp": "GET",
    "/console/api/workspaces/current/tools/workflow": "GET",
    # === 探索/应用市场 ===
    "/console/api/explore/apps": "GET",
    "/console/api/explore/apps/{id}": "GET",
    # === 消息/会话 ===
    "/console/api/messages/{id}/more-like-this": "POST",
    "/console/api/messages/{id}/suggested-questions": "GET,POST",
    "/console/api/saved-messages": "GET,POST",
    "/console/api/saved-messages/{id}": "DELETE",
    # === 文件 ===
    "/console/api/files/{id}/preview": "GET",
    "/console/api/files/upload": "POST",
    # === 系统 ===
    "/console/api/features": "GET",
    "/console/api/setup": "GET,POST",
    "/console/api/account": "GET",
}

for ep, methods in METHOD_MAP.items():
    if ep in endpoints:
        endpoints[ep] = methods

# ---------- 4. 未匹配端点标记 ----------
UNKNOWN = []
for ep, methods in endpoints.items():
    if methods is None:
        UNKNOWN.append(ep)

# ---------- 5. 生成 YAML ----------
import datetime
yaml_lines = []
yaml_lines.append("# ========================================================")
yaml_lines.append("# 系统接口清单 - ai-func.ibosssoft.com.cn")
yaml_lines.append("# 平台: 魔改版 Dify (Next.js 前端 + istio-envoy 网关)")
yaml_lines.append("# 注意: 方法与实际以登录后抓包为准 (标注 try)")
yaml_lines.append("# ========================================================")
yaml_lines.append(f"# 生成: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
yaml_lines.append("")
yaml_lines.append("system:")
yaml_lines.append("  name: AI Func 平台 (Dify 魔改版)")
yaml_lines.append("  base_url: http://ai-func.ibosssoft.com.cn")
yaml_lines.append("  gateway: istio-envoy")
yaml_lines.append("  auth: Bearer Token (Authorization header)")
yaml_lines.append("  note: 未认证返回 401 {'code':'unauthorized'}")
yaml_lines.append("")

# 分组
def group_of(ep):
    if "/rag/" in ep or ep.startswith("/rag"): return "rag_pipelines"
    if "/datasets" in ep: return "datasets"
    if "/apps" in ep: return "apps"
    if "/workspaces/current/plugin" in ep: return "plugins"
    if "/workspaces/current/tool" in ep or "/tools/" in ep: return "tools"
    if "/workspaces" in ep: return "workspaces"
    if "/explore" in ep: return "explore"
    if "/messages" in ep or "/saved-messages" in ep: return "conversations"
    if "/files" in ep: return "files"
    if "/features" in ep or "/setup" in ep or "/account" in ep: return "system"
    return "other"

grouped = {}
for ep, methods in sorted(endpoints.items()):
    g = group_of(ep)
    grouped.setdefault(g, []).append((ep, methods))

for gname in ["apps", "datasets", "workspaces", "plugins", "tools",
              "explore", "conversations", "files", "system", "rag_pipelines",
              "other"]:
    items = grouped.get(gname, [])
    if not items:
        continue
    yaml_lines.append(f"# ---- {gname} ----")
    yaml_lines.append(f"{gname}:")
    for ep, methods in items:
        m = methods or "try"
        yaml_lines.append(f"  - path: \"{ep}\"")
        yaml_lines.append(f"    methods: \"{m}\"")
    yaml_lines.append("")

yaml_text = "\n".join(yaml_lines)

out1 = ROOT / "output" / "api_inventory_v2.yaml"
out1.write_text(yaml_text, encoding="utf-8")
interfaces_dir = ROOT / "api_test" / "interfaces"
interfaces_dir.mkdir(parents=True, exist_ok=True)
out2 = interfaces_dir / "ai_func_dify_api.yaml"
out2.write_text(yaml_text, encoding="utf-8")

print(f"接口端点总数: {len(endpoints)}")
print(f"  已推断方法: {len(endpoints) - len(UNKNOWN)}")
print(f"  待验证(try): {len(UNKNOWN)}")
print(f"  YAML: {out2}")
if UNKNOWN:
    print("\n未匹配方法(需登录验证):")
    for u in UNKNOWN:
        print(f"  - {u}")