#!/usr/bin/env python3
"""
基于真实探测结果修正接口清单:
1. 从 ai_func_dify_api.yaml 移除 404 不存在的接口
2. 新增 rag-func (RagFlow) 服务接口
3. 新增 /runtime/console/api 服务接口
4. 输出三服务合并清单 api_test/interfaces/ai_func_platform_api.yaml
"""
import sys, json, yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "api_test" / "interfaces" / "ai_func_platform_api.yaml"
lines = []
def log(m=""):
    lines.append(m)

# ---------- 1. 原 Dify 清单 + 验证结果 ----------
orig = yaml.safe_load((ROOT / "api_test" / "interfaces" / "ai_func_dify_api.yaml").read_text(encoding="utf-8"))
verify = json.loads((ROOT / "output" / "api_verify_result.json").read_text(encoding="utf-8"))
verdict_map = {v["path"]: v for v in verify}

# 保留: VALID / METHOD / DISABLED / OPEN；移除 INVALID
kept_console = []   # (group, path, methods, verdict)
removed = []
for group, items in orig.items():
    if group == "system" or not isinstance(items, list):
        continue
    for item in items:
        path = item["path"]
        v = verdict_map.get(path)
        verdict = v["verdict"] if v else "UNKNOWN"
        if verdict == "INVALID":
            removed.append((group, path, verdict))
            continue
        # 方法修正: 若探测到405但某方法401，保留401的方法
        methods = item.get("methods", "try")
        probed = v["probed"] if v else ""
        methods_fixed = methods
        if v and v["verdict"] == "METHOD":
            ok_methods = []
            for seg in probed.split("; "):
                m, c = seg.split(":", 1)
                try:
                    c = int(c)
                except ValueError:
                    continue
                if c == 401:
                    ok_methods.append(m)
            if ok_methods:
                methods_fixed = ",".join(ok_methods)
        kept_console.append((group, path, methods_fixed, verdict))

log(f"原 Dify 清单: {sum(len(v) for k, v in orig.items() if isinstance(v, list))} 个")
log(f"  保留: {len(kept_console)} 个")
log(f"  移除(404): {len(removed)} 个")
for g, p, v in removed:
    log(f"    - [{g}] {p} ({v})")

# ---------- 2. RagFlow 接口 (基于 ragflow 开源项目已知 API + 探测确认) ----------
# 探测确认存在: /api/v1/datasets, /api/v1/chats, /api/v1/agents
# RagFlow 官方 OpenAPI (/api/v1) — 依据 infiniflow/ragflow api/apps
RAGFLOW = [
    # 认证
    ("auth", "/api/v1/user/login", "POST", "VALID-代码探测"),
    ("auth", "/api/v1/user/register", "POST", "VALID-代码探测"),
    # 数据集
    ("datasets", "/api/v1/datasets", "GET,POST", "VALID-实测401"),
    ("datasets", "/api/v1/datasets/{dataset_id}", "GET,PUT,DELETE", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/documents", "GET,POST", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/documents/{document_id}", "GET,DELETE", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks", "GET,POST", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/documents/{document_id}/content", "GET", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/documents/{document_id}/status", "GET", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/chunks", "GET", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/chunks/{chunk_id}", "GET,PUT,DELETE", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/chunks/{chunk_id}/keywords", "POST", "VALID-代码探测"),
    ("datasets", "/api/v1/datasets/{dataset_id}/retrieval-test", "POST", "VALID-代码探测"),
    # 会话/聊天 (RagFlow 特有 "chat")
    ("chats", "/api/v1/chats", "GET,POST", "VALID-实测401"),
    ("chats", "/api/v1/chats/{chat_id}", "GET,PUT,DELETE", "VALID-代码探测"),
    ("chats", "/api/v1/chats/{chat_id}/sessions", "GET,POST", "VALID-代码探测"),
    ("chats", "/api/v1/chats/{chat_id}/sessions/{session_id}", "GET,DELETE", "VALID-代码探测"),
    ("chats", "/api/v1/chats/{chat_id}/sessions/{session_id}/messages", "GET", "VALID-代码探测"),
    ("chats", "/api/v1/chats/{chat_id}/completions", "POST", "VALID-代码探测"),
    ("chats", "/api/v1/chats/{chat_id}/query", "POST", "VALID-代码探测"),
    # 智能体
    ("agents", "/api/v1/agents", "GET,POST", "VALID-实测401"),
    ("agents", "/api/v1/agents/{agent_id}", "GET,PUT,DELETE", "VALID-代码探测"),
    ("agents", "/api/v1/agents/{agent_id}/sessions", "GET,POST", "VALID-代码探测"),
    ("agents", "/api/v1/agents/{agent_id}/sessions/{session_id}/messages", "GET", "VALID-代码探测"),
    ("agents", "/api/v1/agents/{agent_id}/completions", "POST", "VALID-代码探测"),
    # 知识库检索
    ("retrieval", "/api/v1/retrieval", "POST", "VALID-代码探测"),
]

# ---------- 3. runtime console API (第二个 Dify 服务) ----------
RUNTIME = [
    ("runtime", "/runtime/console/api/apps", "GET", "VALID-实测401"),
    ("runtime", "/runtime/console/api/features", "GET", "VALID-实测401"),
    ("runtime", "/runtime/console/api/datasets", "GET", "VALID-实测401"),
    ("runtime", "/runtime/console/api/explore/apps", "GET", "VALID-实测401"),
]

# ---------- 4. CAS 服务 ----------
CAS = [
    ("auth", "/cas/login", "GET,POST", "VALID-代码探测"),
    ("auth", "/cas/logout", "GET", "VALID-代码探测"),
    ("auth", "/cas/serviceValidate", "GET", "VALID-代码探测"),
    ("auth", "/cas/v1/tickets", "POST", "VALID-代码探测"),
    ("auth", "/cas/v1/tickets/{tgt}", "GET,DELETE", "VALID-代码探测"),
]

# ---------- 5. 生成合并 YAML ----------
import datetime
yaml_lines = []
yaml_lines.append("# ================================================================")
yaml_lines.append("# 平台接口清单 (多服务合并) - ibosssoft AI 平台")
yaml_lines.append("# 架构: Dify(ai-func) + RagFlow(rag-func) + CAS(cas-func)")
yaml_lines.append("# 认证: Dify=Bearer token; RagFlow='Authorization' Header; CAS=会话")
yaml_lines.append("# 生成: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
yaml_lines.append("# 说明: Dify 清单含实测过滤(移除404)；RagFlow/CAS 基于开源代码+实测组合")
yaml_lines.append("# ================================================================")
yaml_lines.append("")

yaml_lines.append("platform:")
yaml_lines.append("  name: ibosssoft AI 功能平台")
yaml_lines.append("  services:")
yaml_lines.append("    - name: ai-func (Dify 魔改)")
yaml_lines.append("      base_url: http://ai-func.ibosssoft.com.cn")
yaml_lines.append("      auth: \"Authorization: Bearer <token>\"")
yaml_lines.append("      note: 未认证 401 {'code':'unauthorized'}")
yaml_lines.append("    - name: rag-func (RagFlow 魔改)")
yaml_lines.append("      base_url: http://rag-func.ibosssoft.com.cn")
yaml_lines.append("      auth: \"Authorization: Bearer <api_key>\"")
yaml_lines.append("      note: \"未认证 code:0; 无效key code:109\"")
yaml_lines.append("    - name: cas-func (CAS SSO)")
yaml_lines.append("      base_url: http://cas-func.ibosssoft.com.cn")
yaml_lines.append("      auth: TGT/TGC Cookie 会话")
yaml_lines.append("")

# Dify console (实测保留)
yaml_lines.append("dify_console:   # ai-func /console/api/* (实测)") 
cur = None
for group, path, methods, verdict in sorted(kept_console, key=lambda x: (x[0], x[1])):
    if cur != group:
        yaml_lines.append(f"  # group: {group}")
        cur = group
    yaml_lines.append(f"  - path: \"{path}\"")
    yaml_lines.append(f"    methods: \"{methods}\"")
    yaml_lines.append(f"    verified: \"{verdict}\"")
yaml_lines.append("")

# Dify runtime
yaml_lines.append("dify_runtime:   # ai-func /runtime/console/api/* (实测, 独立服务)")
for group, path, methods, verdict in RUNTIME:
    yaml_lines.append(f"  - path: \"{path}\"")
    yaml_lines.append(f"    methods: \"{methods}\"")
    yaml_lines.append(f"    verified: \"{verdict}\"")
yaml_lines.append("")

# RagFlow
yaml_lines.append("ragflow:        # rag-func /api/v1/* (RagFlow 魔改)")
cur = None
for group, path, methods, verdict in RAGFLOW:
    if cur != group:
        yaml_lines.append(f"  # group: {group}")
        cur = group
    yaml_lines.append(f"  - path: \"{path}\"")
    yaml_lines.append(f"    methods: \"{methods}\"")
    yaml_lines.append(f"    verified: \"{verdict}\"")
yaml_lines.append("")

# CAS
yaml_lines.append("cas:            # cas-func /cas/*")
for group, path, methods, verdict in CAS:
    yaml_lines.append(f"  - path: \"{path}\"")
    yaml_lines.append(f"    methods: \"{methods}\"")
    yaml_lines.append(f"    verified: \"{verdict}\"")
yaml_lines.append("")

text = "\n".join(yaml_lines)
OUT.write_text(text, encoding="utf-8")

total = len(kept_console) + len(RUNTIME) + len(RAGFLOW) + len(CAS)
log("")
log(f"合并清单已生成: {OUT}")
log(f"  dify_console: {len(kept_console)}")
log(f"  dify_runtime: {len(RUNTIME)}")
log(f"  ragflow:      {len(RAGFLOW)}")
log(f"  cas:          {len(CAS)}")
log(f"  合计: {total}")
print("\n".join(lines))