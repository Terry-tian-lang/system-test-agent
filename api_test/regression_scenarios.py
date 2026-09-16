# -*- coding: utf-8 -*-
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
