"""
API 接口测试模块 (第二把 LLM)

功能:
1. 读取接口清单 YAML (来自系统识别阶段)
2. 用 LLM (qwen3.8-max) 为每个接口生成测试用例
3. 覆盖: 正向、参数边界、异常、鉴权、安全注入、业务规则
4. 输出: 结构化用例 + Excel/JSON
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field, field_validator

from core.logger import logger
from core.llm_client import LLMClient
from core.console import console
from core.offline_llm import guess_module_abbr


# ============================================================
# 数据模型
# ============================================================

class APITestCase(BaseModel):
    """API 测试用例"""
    序号: int = 0
    用例编号: str = ""
    接口: str = ""                          # 接口路径
    接口名称: str = ""                       # 接口业务名称
    HTTP方法: str = "GET"                   # GET/POST/PUT/PATCH/DELETE
    优先级: str = "P1"
    用例标题: str = ""
    前置条件: str = ""
    请求头: str = ""                        # JSON 字符串
    请求参数: str = ""                      # JSON 字符串
    操作步骤: str = ""
    预期结果: str = ""
    实际结果: str = ""
    备注: str = ""
    关联需求: str = ""

    @field_validator("HTTP方法")
    @classmethod
    def fix_method(cls, v: str) -> str:
        return v.strip().upper()

    def to_excel_row(self) -> List[Any]:
        return [self.序号, self.用例编号, self.接口, self.接口名称,
                self.HTTP方法, self.优先级, self.用例标题, self.前置条件,
                self.请求头, self.请求参数, self.操作步骤, self.预期结果,
                self.实际结果, self.备注, self.关联需求]


class APIInterface(BaseModel):
    """单个接口定义"""
    path: str
    methods: str = "try"
    group: str = "other"
    name: str = ""


# ============================================================
# API 测试用例生成器 (LLM)
# ============================================================

API_CASE_HEADERS = [
    "序号", "用例编号", "接口", "接口名称", "HTTP方法", "优先级",
    "用例标题", "前置条件", "请求头", "请求参数", "操作步骤",
    "预期结果", "实际结果", "备注", "关联需求",
]

SYSTEM_PROMPT = """你是一名资深接口测试工程师，擅长 RESTful API 测试设计。
现提供一个系统的接口清单，请为每个接口设计测试用例。

测试方法要求：
1. 正向用例：正确的参数组合，验证成功场景（200/201）
2. 参数用例：必填缺失、类型错误、边界值（空串、超长、越界、特殊字符）
3. 认证用例：无Token、过期Token、无效Token、越权（401/403）
4. 安全用例：SQL注入、XSS、路径穿越、IDOR（对象级越权）
5. 业务规则：每个接口的隐含业务约束
6. 幂等性：POST/DELETE 重复提交

优先级规则：
- 涉及删除/关键业务/支付/权限 → P0
- 核心增删改查 → P1
- 边界与异常 → P2
- 兼容与负向细节 → P3

输出必须为合法 JSON，结构：
{
  "cases": [
    {
      "接口": "/console/api/datasets",
      "接口名称": "创建数据集",
      "HTTP方法": "POST",
      "优先级": "P1",
      "用例标题": "...",
      "前置条件": "...",
      "请求头": "{\"Content-Type\": \"application/json\", \"Authorization\": \"Bearer <token>\"}",
      "请求参数": "{\"name\": \"测试数据集\", \"indexing_technique\": \"high_quality\", ...}",
      "操作步骤": "1. ...\\n2. ...",
      "预期结果": "1. ...",
      "备注": "测试方法说明",
      "关联需求": "接口文档编号"
    }
  ]
}
注意：请求头/请求参数必须是合法 JSON 字符串；步骤和结果用换行符分隔。"""


class APITestCaseGenerator:
    """API 测试用例生成器（第二把 LLM）"""

    def __init__(self, config=None):
        self.llm = LLMClient(config)
        self.config = config

    def generate(self, interfaces: List[APIInterface], batch_size: int = 8) -> List[APITestCase]:
        """
        为接口清单生成全部测试用例
        :param interfaces: 接口列表
        :param batch_size: 每次LLM调用处理的接口数（避免上下文过长）
        """
        if not interfaces:
            logger.warning("接口清单为空")
            return []

        all_cases: List[APITestCase] = []
        counter = 1

        # 分批处理
        for i in range(0, len(interfaces), batch_size):
            batch = interfaces[i:i + batch_size]
            logger.info(f"正在生成接口批次 {i//batch_size + 1} ({len(batch)} 个接口)...")

            try:
                batch_cases = self._generate_batch(batch)
                for c in batch_cases:
                    c.序号 = counter
                    counter += 1
                all_cases.extend(batch_cases)
                logger.info(f"  批次完成: {len(batch_cases)} 条用例")
            except Exception as e:
                logger.error(f"批次 {i//batch_size + 1} 生成失败: {str(e)[:200]}")
                continue

        logger.info(f"API 测试用例生成完成: 共 {len(all_cases)} 条")
        return all_cases

    def _generate_batch(self, interfaces: List[APIInterface]) -> List[APITestCase]:
        """生成一批接口的用例"""
        # 构造接口清单描述
        desc_lines = []
        for idx, iface in enumerate(interfaces, 1):
            desc_lines.append(f"{idx}. [{iface.methods}] {iface.path}  ({iface.group} - {iface.name})")
        interface_desc = "\n".join(desc_lines)

        prompt = f"""请为以下接口设计测试用例：

## 接口清单
{interface_desc}

## 要求
- 每个接口至少3条用例（正向、认证、异常各至少1条），核心接口可更多
- 无Token/无效Token用例：请求头用 "Authorization": "" 或不带
- 未知的接口参数可合理推断（参考RESTful规范与Dify常见结构）
- 输出为JSON对象，键名为 cases，值为测试用例数组，不要markdown代码块标记"""

        data = self.llm.chat_json([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])

        cases_data = data.get("cases", [])
        cases = []
        for raw in cases_data:
            try:
                case = APITestCase(
                    用例编号="",
                    接口=raw.get("接口", ""),
                    接口名称=raw.get("接口名称", ""),
                    HTTP方法=raw.get("HTTP方法", "GET"),
                    优先级=str(raw.get("优先级", "P2")).upper(),
                    用例标题=raw.get("用例标题", ""),
                    前置条件=raw.get("前置条件", ""),
                    请求头=raw.get("请求头", ""),
                    请求参数=raw.get("请求参数", ""),
                    操作步骤=raw.get("操作步骤", ""),
                    预期结果=raw.get("预期结果", ""),
                    实际结果="",
                    备注=raw.get("备注", ""),
                    关联需求=raw.get("关联需求", ""),
                )
                # 生成用例编号: TC-{组缩写}-{序号}
                abbr = guess_module_abbr(case.接口.split("/")[-1] or case.接口名称)
                case.用例编号 = f"API-{abbr or 'IF'}-{len(cases)+1:03d}"
                cases.append(case)
            except Exception as e:
                logger.warning(f"单条用例解析失败: {e}")
                continue

        return cases

    def export_excel(self, cases: List[APITestCase], output_path: str = None,
                     project_name: str = "API接口测试") -> str:
        """导出为 Excel"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        if not cases:
            logger.warning("无用例可导出")
            return ""

        wb = Workbook()
        ws = wb.active
        ws.title = "API测试用例"

        # 表头
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        for col, h in enumerate(API_CASE_HEADERS, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # 数据
        thin = Side(style="thin")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        prio_colors = {"P0": "FF4444", "P1": "FF9900", "P2": "FFDD00", "P3": "99CC00"}

        for row_idx, case in enumerate(cases, 2):
            for col, val in enumerate(case.to_excel_row(), 1):
                cell = ws.cell(row=row_idx, column=col, value=val)
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                cell.border = border
                if col == 6 and val in prio_colors:
                    cell.fill = PatternFill(start_color=prio_colors[val],
                                            end_color=prio_colors[val], fill_type="solid")
                    cell.font = Font(bold=True)

        # 列宽
        widths = [6, 14, 40, 16, 10, 6, 40, 30, 30, 30, 40, 40, 18, 25, 12]
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

        ws.freeze_panes = "A2"
        ws.auto_filter.ref = f"A1:O{len(cases)+1}"

        # 摘要 sheet
        ws2 = wb.create_sheet("摘要")
        ws2["A1"] = f"{project_name} - API测试用例摘要"
        ws2["A1"].font = Font(bold=True, size=14)
        ws2["A3"] = "总用例数"; ws2["B3"] = len(cases)
        from collections import Counter
        pc = Counter(c.优先级 for c in cases)
        mc = Counter(c.HTTP方法 for c in cases)
        ic = Counter(c.接口 for c in cases)
        ws2["A5"] = "HTTP方法分布"; ws2["A6"] = str(dict(mc))
        ws2["A8"] = "优先级分布"; ws2["A9"] = str(dict(pc))
        ws2["A11"] = "接口分布"; ws2["A12"] = str(dict(ic))

        if output_path is None:
            from datetime import datetime
            from config.loader import get_config
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(output_dir / f"{project_name}_API用例_{ts}.xlsx")

        wb.save(output_path)
        logger.info(f"API 测试用例 Excel 已保存: {output_path}")
        return output_path


def load_interfaces_from_yaml(yaml_path: str) -> List[APIInterface]:
    """从接口清单 YAML 加载接口"""
    import yaml
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    interfaces = []
    if not isinstance(data, dict):
        return interfaces

    # system 段后按分组遍历
    for group, items in data.items():
        if group == "system" or not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and "path" in item:
                interfaces.append(APIInterface(
                    path=item["path"],
                    methods=item.get("methods", "try"),
                    group=group,
                    name=item.get("name", ""),
                ))
    return interfaces


def run_api_case_generation(interfaces_yaml: str = None,
                            output_path: str = None,
                            project_name: str = "知识库平台") -> str:
    """
    完整流程: 加载接口清单 → LLM生成用例 → 导出Excel
    :return: Excel 路径
    """
    if interfaces_yaml is None:
        interfaces_yaml = str(Path(__file__).parent / "interfaces" / "ai_func_dify_api.yaml")

    console.print(f"[bold]接口清单: {interfaces_yaml}[/bold]")
    interfaces = load_interfaces_from_yaml(interfaces_yaml)
    console.print(f"[bold]加载接口 {len(interfaces)} 个[/bold]")

    gen = APITestCaseGenerator()
    cases = gen.generate(interfaces)
    if not cases:
        raise RuntimeError("未生成任何用例，LLM 调用可能失败")

    excel = gen.export_excel(cases, output_path, project_name)
    console.print(f"[bold green]API 用例已导出: {excel}[/bold green]")
    return excel


if __name__ == "__main__":
    run_api_case_generation()