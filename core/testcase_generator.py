"""
测试用例生成模块 - 基于结构化需求生成测试用例
"""
import json
from typing import List, Dict, Any, Optional
from core.logger import logger
from pydantic import BaseModel, Field

from config.loader import get_config
from core.llm_client import LLMClient
from core.requirement_analyzer import RequirementItem


class TestCase(BaseModel):
    """测试用例数据模型"""
    序号: int = Field(default=0, description="序号")
    用例编号: str = Field(default="", description="用例编号，如 TC-LOGIN-001")
    模块: str = Field(default="", description="所属模块")
    优先级: str = Field(default="P2", description="优先级 P0/P1/P2/P3")
    类型: str = Field(default="功能测试", description="测试类型")
    用例标题: str = Field(default="", description="用例标题")
    前置条件: str = Field(default="", description="前置条件")
    操作步骤: str = Field(default="", description="操作步骤")
    预期结果: str = Field(default="", description="预期结果")
    实际结果: str = Field(default="", description="实际结果（执行时填写）")
    备注: str = Field(default="", description="备注")
    关联需求: str = Field(default="", description="关联需求编号")

    def to_excel_row(self) -> List[str]:
        """转换为 Excel 行数据"""
        return [
            self.序号,
            self.用例编号,
            self.模块,
            self.优先级,
            self.类型,
            self.用例标题,
            self.前置条件,
            self.操作步骤,
            self.预期结果,
            self.实际结果,
            self.备注,
            self.关联需求,
        ]


class TestCaseGenerator:
    """测试用例生成器 - 使用 LLM 生成测试用例"""

    def __init__(self, config=None):
        self.config = config or get_config()
        self.llm = LLMClient(self.config)
        self.model = self.llm.model
        self.tc_config = self.config.get_testcase_config()

    def generate(self, requirements: List[RequirementItem]) -> List[TestCase]:
        """
        根据需求列表生成测试用例
        :param requirements: 结构化需求列表
        :return: 测试用例列表
        """
        if not requirements:
            logger.warning("没有需求数据，无法生成测试用例")
            return []

        logger.info(f"开始为 {len(requirements)} 条需求生成测试用例...")

        # 按模块分组需求
        module_reqs = {}
        for req in requirements:
            if req.module not in module_reqs:
                module_reqs[req.module] = []
            module_reqs[req.module].append(req)

        all_cases = []
        case_counter = 1
        failures = []

        for module_name, reqs in module_reqs.items():
            logger.info(f"正在生成模块 [{module_name}] 的测试用例...")
            try:
                cases = self._generate_for_module(module_name, reqs, case_counter)
                all_cases.extend(cases)
                case_counter += len(cases)
            except Exception as e:
                logger.error(f"模块 [{module_name}] 生成失败: {str(e)[:200]}")
                failures.append((module_name, str(e)[:200]))

        # 全部模块失败 → 抛错，避免静默产出空表
        if failures and not all_cases:
            detail = "; ".join(f"{m}: {e}" for m, e in failures)
            raise RuntimeError(f"所有模块的测试用例生成均失败 -> {detail}")

        if failures:
            logger.warning(f"有 {len(failures)} 个模块生成失败，已跳过: "
                           f"{[m for m, _ in failures]}")

        # 更新序号
        for i, case in enumerate(all_cases, 1):
            case.序号 = i

        logger.info(f"共生成 {len(all_cases)} 条测试用例")
        return all_cases

    def _generate_for_module(self, module_name: str,
                              requirements: List[RequirementItem],
                              start_counter: int) -> List[TestCase]:
        """为单个模块生成测试用例"""
        prompt = self._build_generation_prompt(module_name, requirements)

        data = self.llm.chat_json([
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": prompt},
        ])

        cases = self._parse_cases(data, module_name, start_counter)
        logger.info(f"模块 [{module_name}] 生成 {len(cases)} 条用例")
        return cases

    def _system_prompt(self) -> str:
        return """你是一个资深的软件测试工程师，擅长根据需求文档设计高质量的测试用例。
你需要运用以下测试设计方法：
1. 等价类划分 - 有效等价类和无效等价类
2. 边界值分析 - 边界值和边界附近的值
3. 判定表 - 多条件组合的业务规则
4. 状态迁移 - 状态变化的测试
5. 场景法 - 基本流、备选流、异常流
6. 错误推测 - 常见错误和边界情况

你的测试用例必须：
- 覆盖正向场景和反向场景
- 包含边界值和异常输入
- 预期结果具体、可验证
- 步骤清晰、可执行
- 优先级合理分配

请以 JSON 格式返回测试用例。"""

    def _build_generation_prompt(self, module_name: str,
                                  requirements: List[RequirementItem]) -> str:
        req_texts = []
        for req in requirements:
            req_texts.append(f"""
### {req.req_id}: {req.title}
- **优先级**: {req.priority}
- **描述**: {req.description}
- **验收标准**: {req.acceptance_criteria}
""")

        case_types = self.tc_config.get("case_types", ["功能测试"])
        design_methods = self.tc_config.get("design_methods", [])

        return f"""请为模块 [{module_name}] 设计完整的测试用例。

## 需求列表：
{"".join(req_texts)}

## 要求：
1. 测试类型覆盖: {", ".join(case_types)}
2. 设计方法: {", ".join(design_methods)}
3. 每个需求至少生成 3-5 条测试用例
4. 必须包含正向测试、反向测试和边界值测试
5. 优先级分布: P0(10%), P1(30%), P2(40%), P3(20%)

## 输出 JSON 格式：
```json
{{
  "module": "{module_name}",
  "test_cases": [
    {{
      "case_id": "TC-XXX-001",
      "priority": "P0",
      "type": "功能测试",
      "title": "用例标题 - 简洁描述测试目的",
      "preconditions": "前置条件 - 执行该用例前需要满足的条件",
      "steps": "操作步骤\\n1. 第一步操作\\n2. 第二步操作\\n3. 第三步操作",
      "expected_result": "预期结果 - 具体可验证的期望输出/行为",
      "notes": "备注 - 使用的测试方法或特殊说明",
      "related_req": "关联需求ID"
    }}
  ]
}}
```

## 用例编号规则：
- 格式: TC-[模块缩写]-[序号]
- 模块缩写使用模块名称的大写英文缩写（2-4个字母）
- 序号三位数，从 001 开始

请确保测试用例质量高、覆盖全面、可直接用于测试执行。"""

    def _parse_cases(self, data: Dict[str, Any], module_name: str,
                     start_counter: int) -> List[TestCase]:
        """解析已反序列化的测试用例数据"""
        from core.offline_llm import guess_module_abbr
        abbr = guess_module_abbr(module_name)
        cases = []

        for i, tc in enumerate(data.get("test_cases", []), start_counter):
            case = TestCase(
                序号=i,
                用例编号=tc.get("case_id") or f"TC-{abbr}-{i:03d}",
                模块=tc.get("module") or module_name,
                优先级=str(tc.get("priority", "P2")).upper(),
                类型=tc.get("type", "功能测试"),
                用例标题=tc.get("title", ""),
                前置条件=tc.get("preconditions", ""),
                操作步骤=tc.get("steps", ""),
                预期结果=tc.get("expected_result", ""),
                实际结果="",
                备注=tc.get("notes", ""),
                关联需求=tc.get("related_req", ""),
            )
            cases.append(case)

        return cases


def generate_test_cases(requirements: List[RequirementItem]) -> List[TestCase]:
    """
    便捷函数：根据需求生成测试用例
    """
    generator = TestCaseGenerator()
    return generator.generate(requirements)
