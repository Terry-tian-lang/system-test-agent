"""
需求分析模块 - 读取并分析需求文档，提取结构化需求点
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.logger import logger

from config.loader import get_config
from core.doc_loader import load_document_text
from core.llm_client import LLMClient


class RequirementItem:
    """单条需求项"""

    def __init__(self, req_id: str, module: str, title: str,
                 description: str, priority: str = "P1",
                 acceptance_criteria: str = ""):
        self.req_id = req_id
        self.module = module
        self.title = title
        self.description = description
        self.priority = priority
        self.acceptance_criteria = acceptance_criteria

    def to_dict(self) -> Dict[str, str]:
        return {
            "req_id": self.req_id,
            "module": self.module,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "acceptance_criteria": self.acceptance_criteria,
        }


class RequirementAnalyzer:
    """需求分析器 - 使用 LLM 分析需求文档"""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.llm = LLMClient(self.config)
        self.model = self.llm.model

    def load_requirement_text(self, source: str) -> str:
        """
        加载需求文本
        :param source: 文件路径或直接文本内容
        :return: 需求文本
        """
        path = Path(source)
        if path.exists() and path.is_file():
            try:
                text = load_document_text(path)
                logger.info(f"已加载需求文件: {path.name} ({len(text)} 字符)")
                return text
            except Exception as e:
                logger.error(f"加载需求文件失败: {path.name}: {e}")
                raise
        else:
            # 作为直接文本输入
            logger.info(f"使用直接文本输入 ({len(source)} 字符)")
            return source

    def analyze(self, requirement_text: str) -> List[RequirementItem]:
        """
        使用 LLM 分析需求文本，提取结构化需求点
        :param requirement_text: 原始需求文本
        :return: 结构化需求列表
        """
        logger.info("开始需求分析...")

        prompt = self._build_analysis_prompt(requirement_text)

        try:
            data = self.llm.chat_json([
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt},
            ])
            logger.info("LLM 返回分析结果")

            requirements = self._parse_data(data)
            logger.info(f"成功提取 {len(requirements)} 条需求点")
            return requirements

        except Exception as e:
            logger.error(f"需求分析失败: {e}")
            raise

    def _system_prompt(self) -> str:
        return """你是一个专业的软件测试需求分析师。你的任务是分析需求文档，提取结构化的需求点。
你需要：
1. 识别所有功能模块
2. 提取每条需求的详细信息
3. 评估每条需求的优先级 (P0/P1/P2/P3)
4. 明确验收标准

你必须以 JSON 格式返回结果。"""

    def _build_analysis_prompt(self, text: str) -> str:
        return f"""请分析以下需求文档，提取所有需求点。

## 需求文档内容：
{text}

## 输出要求：
请以 JSON 格式返回，结构如下：
```json
{{
  "project_name": "项目名称",
  "modules": [
    {{
      "module_name": "模块名称",
      "requirements": [
        {{
          "req_id": "REQ-001",
          "title": "需求标题",
          "description": "需求详细描述，包括输入、处理逻辑、输出",
          "priority": "P0/P1/P2/P3",
          "acceptance_criteria": "验收标准，可验证的具体条件",
          "business_rules": ["业务规则1", "业务规则2"],
          "edge_cases": ["边界情况1", "边界情况2"],
          "related_reqs": ["关联需求ID"]
        }}
      ]
    }}
  ],
  "summary": {{
    "total_requirements": 0,
    "modules_count": 0,
    "risk_areas": ["高风险区域说明"]
  }}
}}
```

## 优先级定义：
- P0: 核心功能，系统不可用级别
- P1: 重要功能，主要业务流程
- P2: 一般功能，辅助功能
- P3: 低优先级，美化类需求

请确保：
1. 不遗漏任何功能点
2. 每条需求都有明确的验收标准
3. 识别边界情况和异常场景
4. 标注需求之间的关联关系"""

    def _parse_data(self, data: Dict[str, Any]) -> List[RequirementItem]:
        """解析已反序列化的需求分析结果"""
        requirements = []

        for module in data.get("modules", []):
            module_name = module.get("module_name", "未知模块")
            for req in module.get("requirements", []):
                item = RequirementItem(
                    req_id=req.get("req_id", f"REQ-{len(requirements)+1:03d}"),
                    module=module_name,
                    title=req.get("title", ""),
                    description=req.get("description", ""),
                    priority=str(req.get("priority", "P2")).upper(),
                    acceptance_criteria=req.get("acceptance_criteria", ""),
                )
                requirements.append(item)

        return requirements


def analyze_requirements(source: str) -> List[RequirementItem]:
    """
    便捷函数：分析需求并返回结构化结果
    :param source: 文件路径或需求文本
    :return: 需求列表
    """
    analyzer = RequirementAnalyzer()
    text = analyzer.load_requirement_text(source)
    return analyzer.analyze(text)
