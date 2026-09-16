#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拆分 regression_scenarios.py 的 SCENARIOS 为:
   scenarios_agent.py -> SCENARIOS (Agent-xxx 部分)
   scenarios_rag.py   -> SCENARIOS (RAG-xxx 部分)
   原文件改为聚合导入 (兼容 regression_runner 等现有代码)
"""
import ast
import io
import pprint
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "api_test" / "regression_scenarios.py"
assert SRC.exists(), f"缺少源文件: {SRC}"

# 1) 用 AST 提取 SCENARIOS 字典 (保序)
tree = ast.parse(SRC.read_text(encoding="utf-8"))
sc = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "SCENARIOS":
                sc = ast.literal_eval(node.value)
if not sc:
    sys.exit("未找到 SCENARIOS 赋值")

print(f"总场景: {len(sc)}")
agents = {k: v for k, v in sc.items() if k.startswith("Agent")}
rags = {k: v for k, v in sc.items() if k.startswith("RAG")}
print(f"  Agent: {len(agents)}   RAG: {len(rags)}")
assert len(agents) + len(rags) == len(sc), "存在无法归属的用例!"

HEADER = '''# -*- coding: utf-8 -*-
"""回归场景 - {label}
数据来源: {src}
由 tools/split_scenarios.py 从 regression_scenarios.py 拆分生成。
如需调整场景: 请修改本文件后执行 python tools/split_scenarios.py 重新拆分。
"""
from pathlib import Path

THIS_DIR = Path(__file__).parent
'''

def dump_dict(d: dict) -> str:
    # 生成 "    \"Agent-001\": {...},\n" 形式的字典体 (缩进4, 可读)
    body = pprint.pformat(d, width=110, sort_dicts=False)
    return body

def write_scenario_file(path: Path, label: str, src: str, data: dict):
    content = HEADER.format(label=label, src=src)
    content += "SCENARIOS = {\n"
    # pformat 输出 "{...}" -> 去掉首尾花括号, 每行加4空格缩进
    inner = pprint.pformat(data, width=110, sort_dicts=False)
    for line in inner[1:-1].splitlines():
        content += "    " + line + "\n"
    content += "}\n"
    path.write_text(content, encoding="utf-8")

# 2) 生成 scenarios_agent.py / scenarios_rag.py
write_scenario_file(HERE.parent / "api_test" / "scenarios_agent.py",
                    "智能体平台 (Agent-xxx, 74条)", "智能体平台开发态-主流程回归测试用例.xlsx", agents)
print("已生成 api_test/scenarios_agent.py")
write_scenario_file(HERE.parent / "api_test" / "scenarios_rag.py",
                    "知识库平台 (RAG-xxx, 57条)", "知识库平台-主流程回归测试用例.xlsx", rags)
print("已生成 api_test/scenarios_rag.py")

# 3) 重写 regression_scenarios.py 为聚合导入
agg = '''# -*- coding: utf-8 -*-
"""
回归场景聚合入口 (全量 = Agent + RAG)
数据实际存放:
  - api_test/scenarios_agent.py  (Agent-xxx)
  - api_test/scenarios_rag.py    (RAG-xxx)
本文件兼容旧代码: from regression_scenarios import SCENARIOS, load_all
"""
from pathlib import Path

from scenarios_agent import SCENARIOS as _AGENT
from scenarios_rag import SCENARIOS as _RAG

_SCENARIOS = {}
_SCENARIOS.update(_AGENT)
_SCENARIOS.update(_RAG)
SCENARIOS = _SCENARIOS

_THIS = Path(__file__).parent
PLATFORM_YAML = _THIS / "interfaces" / "ai_func_platform_api.yaml"

# 默认 BASE 映射: 未指定 base 的步骤使用
SERVICE_BASE = {
    "dify": "http://ai-func.ibosssoft.com.cn",
    "ragflow": "http://rag-func.ibosssoft.com.cn",
    "cas": "http://cas-func.ibosssoft.com.cn",
}


def load_all():
    """返回 (scenarios, meta)"""
    return SCENARIOS, {"service_base": SERVICE_BASE, "platform_yaml": str(PLATFORM_YAML)}


if __name__ == "__main__":
    sc, meta = load_all()
    n_api = sum(1 for s in sc.values() if s["tag"] != "UI")
    n_ui = sum(1 for s in sc.values() if s["tag"] == "UI")
    n_steps = sum(len(s["steps"]) for s in sc.values())
    print(f"场景总数: {len(sc)} (API/MIX可执行: {n_api}, 纯UI: {n_ui})")
    print(f"接口步骤总数: {n_steps}")
    paths = set()
    for s in sc.values():
        for st in s["steps"]:
            paths.add(st["path"])
    print(f"覆盖接口路径数: {len(paths)}")
'''
(SRC).write_text(agg, encoding="utf-8")
print("regression_scenarios.py 已改为聚合入口")

# 4) 验证聚合结果与原数据一致
sys.path.insert(0, str(HERE.parent / "api_test"))
import scenarios_agent, scenarios_rag
import regression_scenarios as merged
assert len(merged.SCENARIOS) == len(sc), f"数量不符 {len(merged.SCENARIOS)} != {len(sc)}"
assert merged.SCENARIOS == sc, "内容不一致!"
print(f"✅ 聚合验证通过: {len(merged.SCENARIOS)} 条与拆分前完全一致")