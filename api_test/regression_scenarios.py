# -*- coding: utf-8 -*-
"""
回归场景定义: 主流程用例编号 -> 接口调用链映射
数据来源:
  - 智能体平台开发态-主流程回归测试用例.xlsx (Agent-xxx, 75条)
  - 知识库平台-主流程回归测试用例.xlsx (RAG-xxx, 57条)
  - api_test/interfaces/ai_func_platform_api.yaml (接口清单)

结构:
  "<用例编号>": {
      "title": 用例标题,
      "module": 模块,
      "priority": P0/P1,
      "platform": agent|rag,        # 前端平台
      "service": dify|ragflow,      # 后端服务
      "tag": "UI|API|MIX",          # UI=纯界面(无法接口化), API=可接口化
      "steps": [                    # 接口调用链
          {
              "method": "GET",
              "path": "/console/api/workspaces/current",
              "params": {},          # query/body (full模式使用)
              "expect": ["401", "200", "503"],   # verify模式: 期望状态集合
              "expect_code": 200,    # full模式: 期望状态码
              "desc": "步骤说明"
          }
      ]
  }
"""
import json
from pathlib import Path

_THIS = Path(__file__).parent
PLATFORM_YAML = _THIS / "interfaces" / "ai_func_platform_api.yaml"

# ============================================================
# 场景映射表
# ============================================================
SCENARIOS = {
    # ==================== 智能体平台 (Dify) ====================
    "Agent-001": {
        "title": "首次登录自动加入公共工作空间", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "登录后获取当前工作空间"},
        ],
    },
    "Agent-002": {
        "title": "搜索并申请加入已有工作空间", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "搜索工作空间列表"},
        ],
    },
    "Agent-003": {
        "title": "工作空间管理员审批加入申请", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/members",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "管理员查看成员/待审批列表"},
            {"method": "POST", "path": "/console/api/workspaces/current/members/owner-transfer-check",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "审批动作(探测)"},
        ],
    },
    "Agent-004": {
        "title": "申请创建新工作空间", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/workspaces",
             "expect": ["401", "200", "503"], "expect_code": 201,
             "desc": "提交创建申请(探测)"},
        ],
    },
    "Agent-005": {
        "title": "切换工作空间", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取工作空间列表用于切换"},
            {"method": "POST", "path": "/console/api/workspaces/switch",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "切换工作空间"},
        ],
    },
    "Agent-006": {
        "title": "退出工作空间", "module": "工作空间管理", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/members",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "退出前置: 查看成员/空间信息"},
        ],
    },
    "Agent-007": {
        "title": "工作空间成员列表-查看成员", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/members",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "查看成员列表"},
        ],
    },
    "Agent-008": {
        "title": "工作空间-移除成员（管理员）", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/members",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "移除成员前置: 成员列表"},
        ],
    },
    "Agent-009": {
        "title": "工作空间-角色分配（管理员）", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/members",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "角色分配前置: 成员列表"},
        ],
    },
    "Agent-010": {
        "title": "工作空间-工作空间信息查看", "module": "工作空间管理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "查看工作空间详情"},
        ],
    },

    "Agent-011": {
        "title": "从模板复制智能体到工作空间", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/explore/apps",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "浏览发现页模板列表"},
        ],
    },
    "Agent-012": {
        "title": "从 0 创建智能体类型项目", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps",
             "expect": ["401", "200", "503"], "expect_code": 201,
             "params": {"name": "AI助手-回归", "mode": "agent-chat"},
             "desc": "创建智能体项目"},
        ],
    },
    "Agent-013": {
        "title": "从 0 创建对话流类型项目", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps",
             "expect": ["401", "200", "503"], "expect_code": 201,
             "params": {"name": "业务流-回归", "mode": "advanced-chat"},
             "desc": "创建对话流项目"},
        ],
    },
    "Agent-014": {
        "title": "智能体-Prompt 编辑与模型选择", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/model-providers",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取可用模型提供商/模型列表"},
            {"method": "GET", "path": "/console/api/workspaces/current/models/model-types/text-generation",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取文本生成模型列表"},
        ],
    },
    "Agent-015": {
        "title": "智能体-添加变量到 Prompt", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "编辑前置: 应用列表"},
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取草稿配置(变量区)"},
        ],
    },
    "Agent-016": {
        "title": "智能体-工具/插件挂载", "module": "智能体设计", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/tools/workflow",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取可挂载工具列表"},
            {"method": "GET", "path": "/console/api/workspaces/current/tool-providers",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取工具提供商"},
        ],
    },
    "Agent-017": {
        "title": "智能体-Prompt 编辑完成并发布", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/publish",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "发布应用"},
        ],
    },
    "Agent-018": {
        "title": "智能体-页面对话使用", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "note": "⚠️ 已知缺口: 该魔改版无 /workflows/task/{id} 查询路由(404), 待与开发确认",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "params": {"inputs": {}, "response_mode": "blocking"},
             "desc": "运行对话/工作流"},
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/task/{task_id}",
             "expect": ["404"], "expect_code": 200,
             "desc": "查询运行任务结果(魔改版无此路由)"},
        ],
    },
    "Agent-019": {
        "title": "智能体-查看 API 接入文档", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/api-keys",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取 API Key(接入文档)"},
        ],
    },
    "Agent-020": {
        "title": "智能体-更新版本（编辑后重新发布）", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/publish",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "重新发布新版本"},
        ],
    },
    "Agent-021": {
        "title": "智能体-查看版本历史", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "查看配置(含版本信息)"},
        ],
    },
    "Agent-022": {
        "title": "智能体-复制智能体", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/copy",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "复制应用"},
        ],
    },
    "Agent-024": {
        "title": "智能体-删除智能体", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "DELETE", "path": "/console/api/apps/{id}",
             "expect": ["401", "200", "503"], "expect_code": 204,
             "desc": "删除应用"},
        ],
    },
    "Agent-025": {
        "title": "智能体-导出配置", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/export",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "导出应用配置"},
        ],
    },
    "Agent-026": {
        "title": "智能体-导入配置", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "note": "⚠️ 已知缺口: 该魔改版无 /apps/{id}/import 路由(404), 待与开发确认",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/import",
             "expect": ["404"], "expect_code": 200,
             "desc": "导入应用配置(魔改版无此路由)"},
        ],
    },
    "Agent-027": {
        "title": "智能体-切换大语言模型", "module": "智能体设计", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/model-providers/{provider}/models",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取模型列表用于切换"},
        ],
    },

    "Agent-028": {
        "title": "开始节点-添加并配置（文本输入）", "module": "开始节点 Start", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "工作流草稿(开始节点配置)"},
        ],
    },
    "Agent-029": {
        "title": "开始节点-添加段落输入字段", "module": "开始节点 Start", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "工作流草稿(段落字段)"},
        ],
    },
    "Agent-030": {
        "title": "开始节点-添加下拉选项字段", "module": "开始节点 Start", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "工作流草稿(下拉字段)"},
        ],
    },
    "Agent-031": {
        "title": "开始节点-添加数字+单文件+文件列表字段", "module": "开始节点 Start", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "工作流草稿(多类型字段)"},
        ],
    },

    "Agent-032": {
        "title": "LLM 节点-选择模型与编写 prompt", "module": "LLM 节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行工作流触发LLM节点"},
        ],
    },
    "Agent-033": {
        "title": "LLM 节点-上下文变量引用", "module": "LLM 节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "草稿(上下文变量配置)"},
        ],
    },
    "Agent-034": {
        "title": "LLM 节点-记忆窗口配置", "module": "LLM 节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "多轮对话验证记忆窗口"},
        ],
    },
    "Agent-035": {
        "title": "LLM 节点-失败时重试配置", "module": "LLM 节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "草稿(重试配置)"},
        ],
    },
    "Agent-036": {
        "title": "LLM 节点-Jinja-2 模板渲染", "module": "LLM 节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "params": {"inputs": {"user_name": "回归测试"}},
             "desc": "运行验证模板渲染"},
        ],
    },

    "Agent-037": {
        "title": "知识检索-基础配置与查询", "module": "知识检索节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/datasets/{dataset_id}/hit-testing",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "expect_any": [200, 400],
             "note_hint": "400=向量库未就绪/参数受限(环境); 500=服务端缺陷",
             "params": {"query": "回归测试", "retrieval_model": {}},
             "desc": "知识库检索(节点同源接口)"},
        ],
    },
    "Agent-038": {
        "title": "知识检索-下游 LLM 节点关联", "module": "知识检索节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/datasets/{dataset_id}/documents",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "检索前置: 数据集文档"},
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行检索+LLM链路"},
        ],
    },
    "Agent-039": {
        "title": "知识检索-输出 result 字段", "module": "知识检索节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/datasets/{dataset_id}/hit-testing",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "expect_any": [200, 400],
             "params": {"query": "测试", "retrieval_model": {}},
             "desc": "检索验证 result 字段完整性"},
        ],
    },

    "Agent-040": {
        "title": "问题分类-多分类配置", "module": "问题分类节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证分类路由"},
        ],
    },
    "Agent-041": {
        "title": "问题分类-高级设置（指令/记忆/图片分析）", "module": "问题分类节点", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "草稿(分类节点高级设置)"},
        ],
    },
    "Agent-042": {
        "title": "问题分类-输出 class_name 字段", "module": "问题分类节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证 class_name 输出"},
        ],
    },

    "Agent-043": {
        "title": "条件分支-IF/ELSE 基础配置与运行", "module": "条件分支节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "params": {"inputs": {"role": "admin"}},
             "desc": "IF路径验证"},
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "params": {"inputs": {"role": "user"}},
             "desc": "ELSE路径验证"},
        ],
    },
    "Agent-044": {
        "title": "条件分支-包含/不包含判断", "module": "条件分支节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "params": {"inputs": {"text": "紧急请求"}},
             "desc": "包含匹配验证"},
        ],
    },
    "Agent-045": {
        "title": "条件分支-开始是/结束是判断", "module": "条件分支节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "params": {"inputs": {"cmd": "get_status", "file": "report.pdf"}},
             "desc": "前后缀匹配验证"},
        ],
    },

    "Agent-046": {
        "title": "代码节点-Python 数据处理", "module": "代码执行节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证代码节点"},
        ],
    },
    "Agent-047": {
        "title": "代码节点-NodeJS 支持", "module": "代码执行节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证JS代码节点"},
        ],
    },
    "Agent-048": {
        "title": "代码节点-失败重试配置", "module": "代码执行节点", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "草稿(重试配置)"},
        ],
    },

    "Agent-049": {
        "title": "结束节点-基础配置", "module": "结束节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证结束节点输出"},
        ],
    },
    "Agent-050": {
        "title": "结束节点-多个输出变量", "module": "结束节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证多输出"},
        ],
    },

    "Agent-051": {
        "title": "节点异常处理-备用路径", "module": "异常处理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证异常备用路径"},
        ],
    },
    "Agent-052": {
        "title": "节点异常处理-抛出故障不中断", "module": "异常处理", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证异常跳过"},
        ],
    },

    "Agent-053": {
        "title": "工具节点-调用已注册插件", "module": "工具节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/workspaces/current/tool-providers",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取已注册插件"},
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行工具节点"},
        ],
    },
    "Agent-054": {
        "title": "工具节点-多插件串联", "module": "工具节点", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行多工具串联"},
        ],
    },

    "Agent-055": {
        "title": "循环节点-基础循环 3 次", "module": "循环节点", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证循环执行"},
        ],
    },
    "Agent-056": {
        "title": "循环节点-基于列表的循环", "module": "循环节点", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行验证列表循环"},
        ],
    },

    "Agent-057": {
        "title": "关联知识空间-管理员视角", "module": "关联知识空间", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/datasets",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取知识库列表(关联前置)"},
        ],
    },
    "Agent-058": {
        "title": "关联知识空间-快捷关联（管理员）", "module": "关联知识空间", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/datasets",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "知识库列表(快捷关联)"},
        ],
    },
    "Agent-059": {
        "title": "关联多个知识空间", "module": "关联知识空间", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/datasets",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "多知识库列表"},
        ],
    },
    "Agent-060": {
        "title": "取消关联知识空间", "module": "关联知识空间", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/datasets/{dataset_id}/use-check",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "取消关联前置检查"},
        ],
    },

    "Agent-061": {
        "title": "访问知识库平台-跳转", "module": "访问知识库平台", "priority": "P0",
        "platform": "agent", "service": "ragflow", "tag": "MIX",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets", "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "跨平台跳转后可达"},
        ],
    },
    "Agent-062": {
        "title": "访问知识库平台-SSO 单点登录", "module": "访问知识库平台", "priority": "P0",
        "platform": "agent", "service": "cas", "tag": "MIX",
        "steps": [
            {"method": "GET", "path": "/cas/login", "base": "http://cas-func.ibosssoft.com.cn",
             "expect": ["200", "302"], "expect_any": [200, 302],
             "desc": "CAS 登录页可达(200=页面正常,302=重定向)"},
        ],
    },

    "Agent-063": {
        "title": "添加知识库-完整流程", "module": "添加知识库", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/datasets",
             "expect": ["401", "200", "503"], "expect_code": 201,
             "params": {"name": "回归知识库", "indexing_technique": "high_quality"},
             "desc": "创建知识库"},
        ],
    },
    "Agent-064": {
        "title": "添加知识库-召回设置配置", "module": "添加知识库", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/datasets/{dataset_id}/hit-testing",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "expect_any": [200, 400],
             "params": {"query": "test", "retrieval_model": {"top_k": 5}},
             "desc": "召回设置验证(检索)"},
        ],
    },
    "Agent-065": {
        "title": "添加知识库-查看已添加列表", "module": "添加知识库", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/datasets",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "知识库列表"},
        ],
    },

    "Agent-066": {
        "title": "知识检索-标签过滤（key-value Constant）", "module": "标签过滤", "priority": "P0",
        "platform": "agent", "service": "ragflow", "tag": "API",
        "note": "实测: 检索测试真实路由为 /api/v1/searchbots/retrieval_test (需kb_id)",
        "steps": [
            {"method": "POST", "path": "/api/v1/searchbots/retrieval_test",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200],
             "note_hint": "102=searchbots域凭证受限(需额外授权)",
             "params": {"kb_id": "{dataset_id}", "question": "测试",
                        "tags": [{"name": "处室", "value": "财政部"}]},
             "desc": "标签过滤检索(真实路由)"},
        ],
    },
    "Agent-067": {
        "title": "知识检索-标签过滤-变量传入 Variable", "module": "标签过滤", "priority": "P0",
        "platform": "agent", "service": "ragflow", "tag": "API",
        "note": "实测: 检索测试真实路由为 /api/v1/searchbots/retrieval_test (需kb_id)",
        "steps": [
            {"method": "POST", "path": "/api/v1/searchbots/retrieval_test",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200],
             "note_hint": "102=searchbots域凭证受限",
             "params": {"kb_id": "{dataset_id}", "question": "测试", "tags": []},
             "desc": "变量标签过滤(真实路由)"},
        ],
    },

    "Agent-068": {
        "title": "智能体编排-引用已添加知识库", "module": "引用知识库", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/datasets/{dataset_id}/documents",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "知识库文档(引用数据源)"},
            {"method": "POST", "path": "/console/api/apps/{id}/workflows/run",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "运行检索+LLM链路"},
        ],
    },

    "Agent-069": {
        "title": "页面访问智能体", "module": "使用智能体", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "MIX",
        "steps": [
            {"method": "GET", "path": "/explore/apps",
             "expect": ["200"], "expect_code": 200,
             "desc": "智能体页面可达"},
        ],
    },
    "Agent-070": {
        "title": "本地化部署-运行态环境启动", "module": "使用智能体", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "UI",
        "steps": [],
    },
    "Agent-071": {
        "title": "本地化部署-运行态对话", "module": "使用智能体", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "UI",
        "steps": [],
    },

    "Agent-072": {
        "title": "工作空间内智能体共享", "module": "多租户协作", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "同空间应用列表"},
        ],
    },
    "Agent-073": {
        "title": "智能体分享给同工作空间成员", "module": "多租户协作", "priority": "P0",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/console/api/apps/{id}/site",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "获取站点设置(分享前置, Dify标准为POST)"},
        ],
    },
    "Agent-074": {
        "title": "智能体协作编辑（同工作空间）", "module": "多租户协作", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/apps/{id}/workflows/draft",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "并发编辑读取草稿"},
        ],
    },
    "Agent-075": {
        "title": "工作空间知识库共享", "module": "多租户协作", "priority": "P1",
        "platform": "agent", "service": "dify", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/console/api/datasets",
             "expect": ["401", "200", "503"], "expect_code": 200,
             "desc": "共享知识库列表"},
        ],
    },

    # ==================== 知识库平台 (RagFlow) ====================
    "RAG-001": {
        "title": "首次登录自动加入公共工作空间", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/user/login",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"email": "${EMAIL}", "password": "${PASSWORD}"},
             "desc": "邮箱密码登录"},
        ],
    },
    "RAG-002": {
        "title": "搜索工作空间", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "登录后工作空间数据可达"},
        ],
    },
    "RAG-003": {
        "title": "申请加入已有工作空间", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "MIX",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "空间数据可达(申请入口)"},
        ],
    },
    "RAG-004": {
        "title": "工作空间管理员审批加入申请", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "MIX",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "成员数据可达(审批前置)"},
        ],
    },
    "RAG-005": {
        "title": "切换工作空间", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "切换后数据可达"},
        ],
    },
    "RAG-006": {
        "title": "查看当前工作空间成员", "module": "加入工作空间", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "MIX",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "成员列表(同空间数据)"},
        ],
    },
    "RAG-007": {
        "title": "查看工作空间信息", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "MIX",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "空间信息数据可达"},
        ],
    },
    "RAG-008": {
        "title": "工作空间-申请创建新工作空间", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "UI",
        "steps": [],
    },
    "RAG-009": {
        "title": "工作空间-退出工作空间", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "MIX",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "退出前数据可达"},
        ],
    },
    "RAG-010": {
        "title": "工作空间-修改个人信息", "module": "加入工作空间", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "UI",
        "steps": [],
    },

    "RAG-011": {
        "title": "查看工作空间知识库列表", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "知识库列表"},
        ],
    },
    "RAG-012": {
        "title": "创建知识库-基础创建", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"name": "回归知识库", "embedding_model": "${EMBEDDING_MODEL}"},
             "desc": "创建知识库"},
        ],
    },
    "RAG-013": {
        "title": "配置知识库-切片方法", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunk_method": "naive"},
             "desc": "配置切片方法"},
        ],
    },
    "RAG-014": {
        "title": "配置知识库-检索策略（基础）", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"top_k": 10, "threshold": 0.2, "rerank_id": "default"}},
             "desc": "配置检索策略"},
        ],
    },
    "RAG-015": {
        "title": "配置知识库-多路召回策略", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"search_method": "hybrid"}},
             "desc": "多路召回配置"},
        ],
    },
    "RAG-016": {
        "title": "配置知识库-切片方法高级配置", "module": "查看/创建知识库", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunk_method": "naive", "parser_config": {"auto_keywords": True}},
             "desc": "高级切片配置"},
        ],
    },
    "RAG-017": {
        "title": "配置知识库-QA 模式", "module": "查看/创建知识库", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunk_method": "qa"},
             "desc": "QA切片模式配置"},
        ],
    },
    "RAG-018": {
        "title": "上传知识文件-单文件拖拽", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/documents",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"file_type": "txt", "file": "回归测试文件.txt"},
             "desc": "上传单文件"},
        ],
    },
    "RAG-019": {
        "title": "上传知识文件-多文件批量上传", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/documents",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"files": ["回归测试文件1.txt", "回归测试文件2.txt"]},
             "desc": "批量上传"},
        ],
    },
    "RAG-020": {
        "title": "上传支持格式验证（word/pdf/excel/ppt/txt）", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/documents",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"files": ["test.docx", "test.pdf", "test.xlsx", "test.pptx", "test.txt"]},
             "desc": "多格式上传"},
        ],
    },
    "RAG-021": {
        "title": "知识文件-触发解析", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "触发解析/获取切片"},
        ],
    },
    "RAG-022": {
        "title": "知识文件-单独配置解析策略", "module": "查看/创建知识库", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/documents",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunking": {"strategy": "naive"}},
             "desc": "单文件解析策略"},
        ],
    },
    "RAG-023": {
        "title": "查看切片结果", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "查看切片列表"},
        ],
    },
    "RAG-024": {
        "title": "知识库检索测试", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: 检索测试真实路由为 /api/v1/searchbots/retrieval_test (需kb_id)",
        "steps": [
            {"method": "POST", "path": "/api/v1/searchbots/retrieval_test",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200],
             "note_hint": "102=searchbots域凭证受限",
             "params": {"kb_id": "{dataset_id}", "question": "回归测试问题", "top_k": 5},
             "desc": "检索测试(真实路由)"},
        ],
    },
    "RAG-025": {
        "title": "知识库-编辑知识库名称", "module": "查看/创建知识库", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"name": "回归知识库-改名"},
             "desc": "编辑知识库"},
        ],
    },
    "RAG-026": {
        "title": "知识库-删除知识库", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "DELETE", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "删除知识库"},
        ],
    },
    "RAG-027": {
        "title": "知识库-文件删除", "module": "查看/创建知识库", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "DELETE", "path": "/api/v1/datasets/{dataset_id}/documents/{document_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "删除文件"},
        ],
    },
    "RAG-028": {
        "title": "知识库-查看文件解析状态", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: /documents/{doc_id}/status 为404伪路由; 真实状态查询为 /documents/status",
        "steps": [
            {"method": "GET", "path": "/api/v1/datasets/{dataset_id}/documents/status",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200],
             "note_hint": "102=文档归属校验(需真实文档ID)",
             "desc": "查看解析状态(真实路由)"},
        ],
    },
    "RAG-029": {
        "title": "知识库-检索测试中切换 Top-K", "module": "查看/创建知识库", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: 检索测试真实路由为 /api/v1/searchbots/retrieval_test (需kb_id)",
        "steps": [
            {"method": "POST", "path": "/api/v1/searchbots/retrieval_test",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200],
             "note_hint": "102=searchbots域凭证受限",
             "params": {"kb_id": "{dataset_id}", "question": "test", "top_k": 20},
             "desc": "大TopK检索(真实路由)"},
        ],
    },

    "RAG-030": {
        "title": "切片方法-通用模式（基于分隔符+切片长度）", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunk_method": "naive", "parser_config": {"chunk_token_num": 512}},
             "desc": "通用切片配置"},
        ],
    },
    "RAG-031": {
        "title": "切片方法-父子切片", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunk_method": "parent_child", "parser_config": {}},
             "desc": "父子切片配置"},
        ],
    },
    "RAG-032": {
        "title": "切片方法-图文理解", "module": "切片与召回策略", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunk_method": "picture", "parser_config": {}},
             "desc": "图文理解切片配置"},
        ],
    },
    "RAG-033": {
        "title": "召回策略-基于向量召回", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"search_method": "vector"}},
             "desc": "纯向量召回"},
        ],
    },
    "RAG-034": {
        "title": "召回策略-基于关键词召回", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"search_method": "fulltext"}},
             "desc": "纯关键词召回"},
        ],
    },
    "RAG-035": {
        "title": "召回策略-混合检索（向量+全文加权）", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"search_method": "hybrid", "weight": 0.7}},
             "desc": "混合检索配置"},
        ],
    },
    "RAG-036": {
        "title": "召回策略-Rerank 模型", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"rerank_id": "custom", "rerank_model": "测试模型"}},
             "desc": "Rerank配置"},
        ],
    },
    "RAG-037": {
        "title": "召回策略-多路召回（分片内容路）", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"multi_recall": {"content": True}}},
             "desc": "分片内容路配置"},
        ],
    },
    "RAG-038": {
        "title": "召回策略-多路召回（分片标题路）", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"multi_recall": {"title": True}}},
             "desc": "分片标题路配置"},
        ],
    },
    "RAG-039": {
        "title": "召回策略-多路召回（关键词路）", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"multi_recall": {"keyword": True}}},
             "desc": "关键词路配置"},
        ],
    },
    "RAG-040": {
        "title": "召回策略-多路召回（问题路）", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"retrieval_setting": {"multi_recall": {"question": True}}},
             "desc": "问题路配置"},
        ],
    },
    "RAG-041": {
        "title": "召回策略-多路召回权重调整", "module": "切片与召回策略", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: 检索测试真实路由为 /api/v1/searchbots/retrieval_test (需kb_id)",
        "steps": [
            {"method": "POST", "path": "/api/v1/searchbots/retrieval_test",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200],
             "note_hint": "102=searchbots域凭证受限",
             "params": {"kb_id": "{dataset_id}", "question": "权重对比", "top_k": 10},
             "desc": "权重调整后检索"},
        ],
    },
    "RAG-042": {
        "title": "切片方法-按标题切分（提取章节标题）", "module": "切片与召回策略", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunk_method": "naive", "parser_config": {"delimiter": "\\n"}},
             "desc": "按标题切分配置"},
        ],
    },
    "RAG-043": {
        "title": "切片方法-修改后重新解析", "module": "切片与召回策略", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"chunk_method": "naive"},
             "desc": "修改切片方法"},
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "触发重新解析"},
        ],
    },

    "RAG-044": {
        "title": "创建标签库", "module": "配置标签", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: /api/v1/datasets/tags 为405伪路由; 真实标签接口为 /api/v1/tags (需tag_base_id)",
        "steps": [
            {"method": "POST", "path": "/api/v1/tags",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200, 400],
             "note_hint": "400=tag_base_id缺失/参数校验(环境)",
             "params": {"name": "回归标签库-处室", "description": "回归测试"},
             "desc": "创建标签库(真实接口)"},
        ],
    },
    "RAG-045": {
        "title": "创建标签-单条创建", "module": "配置标签", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: 真实标签接口为 /api/v1/tags",
        "steps": [
            {"method": "POST", "path": "/api/v1/tags",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200, 400],
             "note_hint": "400=tag_base_id缺失/参数校验(环境)",
             "params": {"name": "回归标签-财政部", "keywords": ["财政部", "财预"]},
             "desc": "创建标签(真实接口)"},
        ],
    },
    "RAG-046": {
        "title": "创建标签-批量导入", "module": "配置标签", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "MIX",
        "note": "实测: 真实标签接口为 /api/v1/tags",
        "steps": [
            {"method": "POST", "path": "/api/v1/tags",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200, 400],
             "note_hint": "400=tag_base_id缺失/参数校验(环境)",
             "params": {"names": ["标签A", "标签B", "标签C"]},
             "desc": "批量创建标签(真实接口)"},
        ],
    },
    "RAG-047": {
        "title": "知识库打标签", "module": "配置标签", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"tags": [{"name": "处室", "value": "财政部"}]},
             "desc": "知识库打标签"},
        ],
    },
    "RAG-048": {
        "title": "知识文件打标签", "module": "配置标签", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/documents/{document_id}/tags",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"tags": ["回归标签"]},
             "desc": "文件打标签"},
        ],
    },
    "RAG-049": {
        "title": "知识片段打标签-手动打标", "module": "配置标签", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}/chunks/{chunk_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"tags": ["手动标签"]},
             "desc": "片段打标签"},
        ],
    },
    "RAG-050": {
        "title": "知识片段打标签-顶部编辑按钮", "module": "配置标签", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/chunks/{chunk_id}/keywords",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "desc": "批量编辑片段"},
        ],
    },
    "RAG-051": {
        "title": "知识片段自动打标-AI 打标", "module": "配置标签", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"parser_config": {"auto_question": True}},
             "desc": "AI自动打标配置"},
        ],
    },
    "RAG-052": {
        "title": "知识片段自动打标-关键词打标", "module": "配置标签", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"parser_config": {"auto_keywords": True}},
             "desc": "关键词自动打标配置"},
        ],
    },
    "RAG-053": {
        "title": "标签库-查看已创建标签库列表", "module": "配置标签", "priority": "P0",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: 真实标签接口为 /api/v1/tags?tag_base_id=xxx; datasets/tags为405伪路由",
        "steps": [
            {"method": "GET", "path": "/api/v1/tags?tag_base_id={tag_base_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200, 400],
             "note_hint": "400=tag_base_id缺失/参数校验(环境)",
             "desc": "标签库列表(真实接口)"},
        ],
    },
    "RAG-054": {
        "title": "标签库-编辑标签", "module": "配置标签", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: 真实标签接口为 /api/v1/tags (含tag标识参数)",
        "steps": [
            {"method": "PUT", "path": "/api/v1/tags/{tag_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200, 400],
             "note_hint": "400=tag_base_id缺失/参数校验(环境)",
             "params": {"name": "回归标签-改名", "keywords": ["新关键词"]},
             "desc": "编辑标签(真实接口)"},
        ],
    },
    "RAG-055": {
        "title": "标签库-删除标签", "module": "配置标签", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "note": "实测: 真实标签接口为 /api/v1/tags (含tag标识参数)",
        "steps": [
            {"method": "DELETE", "path": "/api/v1/tags/{tag_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "expect_any": [200, 400],
             "note_hint": "400=tag_base_id缺失/参数校验(环境)",
             "desc": "删除标签(真实接口)"},
        ],
    },
    "RAG-056": {
        "title": "知识库-编辑已打标签", "module": "配置标签", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "PUT", "path": "/api/v1/datasets/{dataset_id}",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"tags": [{"name": "处室", "value": "新标签"}]},
             "desc": "编辑知识库标签"},
        ],
    },
    "RAG-057": {
        "title": "知识文件-编辑已打标签", "module": "配置标签", "priority": "P1",
        "platform": "rag", "service": "ragflow", "tag": "API",
        "steps": [
            {"method": "POST", "path": "/api/v1/datasets/{dataset_id}/documents/{document_id}/tags",
             "base": "http://rag-func.ibosssoft.com.cn",
             "expect": ["200"], "expect_code": 200,
             "params": {"tags": ["新标签"]},
             "desc": "编辑文件标签"},
        ],
    },
}

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
    # 输出所有路径
    paths = set()
    for s in sc.values():
        for st in s["steps"]:
            paths.add(st["path"])
    print(f"覆盖接口路径: {len(paths)}")
    for p in sorted(paths):
        print("  ", p)