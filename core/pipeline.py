"""
测试流程编排器 - 全流程测试Agent的核心管道
将需求分析、用例生成、执行测试、报告生成串联为完整流程
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.logger import logger
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from config.loader import get_config
from core.console import console
from core.requirement_analyzer import RequirementAnalyzer, RequirementItem
from core.testcase_generator import TestCaseGenerator, TestCase
from core.excel_exporter import ExcelExporter
from core.offline_llm import OfflineRequirementAnalyzer, OfflineTestCaseGenerator


class TestPipeline:
    """全流程测试管道"""

    def __init__(self, config=None, offline: bool = False):
        self.config = config or get_config()
        self.offline = offline
        self.exporter = ExcelExporter(self.config)

        if offline:
            # 离线模式：使用规则引擎，无需 API Key
            self.analyzer = OfflineRequirementAnalyzer()
            self.generator = OfflineTestCaseGenerator()
            console.print("[dim]离线模式已启用 - 使用规则引擎生成，无需 LLM[/dim]")
        else:
            self.analyzer = RequirementAnalyzer(self.config)
            self.generator = TestCaseGenerator(self.config)

        self.requirements: List[RequirementItem] = []
        self.test_cases: List[TestCase] = []
        self.project_name = "系统测试项目"

    def run_step1_requirement_analysis(self, source: str) -> List[RequirementItem]:
        """
        第一步：需求分析
        :param source: 需求来源（文件路径或文本）
        :return: 结构化需求列表
        """
        console.print(Panel("📋 第一步：需求分析", style="bold blue"))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("正在分析需求文档...", total=100)

            # 加载需求文本
            progress.update(task, advance=20, description="正在加载需求文档...")
            text = self._load_text(source)

            # 分析需求
            mode = "规则引擎" if self.offline else "LLM"
            progress.update(task, advance=30, description=f"{mode} 正在分析需求...")
            self.requirements = self.analyzer.analyze(text)

            progress.update(task, advance=50, description="需求分析完成！")

        # 显示结果摘要
        self._show_requirements_summary()
        return self.requirements

    def run_step2_generate_testcases(self, requirements: List[RequirementItem] = None) -> List[TestCase]:
        """
        第二步：生成测试用例
        :param requirements: 需求列表（可选，默认使用上一步的结果）
        :return: 测试用例列表
        """
        reqs = requirements or self.requirements
        console.print(Panel("📝 第二步：生成测试用例", style="bold green"))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("正在生成测试用例...", total=100)

            desc = "正在应用测试设计方法..." if self.offline else "正在构建提示词..."
            progress.update(task, advance=20, description=desc)
            self.test_cases = self.generator.generate(reqs)
            progress.update(task, advance=80, description="测试用例生成完成！")

        # 显示结果摘要
        self._show_testcases_summary()
        return self.test_cases

    def _load_text(self, source: str) -> str:
        """加载需求文本（兼容离线/在线模式、PDF/文本文件）"""
        # 在线模式优先使用带 LLM 的加载器
        loader = getattr(self.analyzer, "load_requirement_text", None)
        if loader is not None:
            return loader(source)

        # 离线模式：走统一文档加载器
        from core.doc_loader import load_document_text
        path = Path(source)
        if path.exists() and path.is_file():
            text = load_document_text(path)
            logger.info(f"已加载需求文件: {path.name} ({len(text)} 字符)")
            return text
        logger.info(f"使用直接文本输入 ({len(source)} 字符)")
        return source

    def run_step3_export_excel(self, test_cases: List[TestCase] = None,
                                output_path: str = None) -> str:
        """
        第三步：导出 Excel
        :param test_cases: 测试用例列表（可选）
        :param output_path: 输出路径（可选）
        :return: 输出文件路径
        """
        cases = test_cases or self.test_cases
        console.print(Panel("📊 第三步：导出 Excel 测试用例", style="bold yellow"))

        result = self.exporter.export(cases, output_path, self.project_name)

        if result:
            console.print(f"  ✅ Excel 已导出: [bold]{result}[/bold]")
        return result

    def run_full_pipeline(self, source: str,
                          output_path: str = None) -> Dict[str, Any]:
        """
        执行完整流程（第一步 ~ 第三步）
        :param source: 需求来源
        :param output_path: Excel 输出路径
        :return: 流程结果摘要
        """
        console.print(Panel(
            f"🚀 全流程测试Agent - {self.project_name}\n"
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            style="bold magenta"
        ))

        # Step 1
        requirements = self.run_step1_requirement_analysis(source)

        # Step 2
        test_cases = self.run_step2_generate_testcases(requirements)

        # Step 3
        excel_path = self.run_step3_export_excel(test_cases, output_path)

        # 汇总
        result = {
            "project_name": self.project_name,
            "requirements_count": len(requirements),
            "test_cases_count": len(test_cases),
            "excel_path": excel_path,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
        }

        self._show_final_summary(result)
        return result

    def _show_requirements_summary(self):
        """显示需求分析结果摘要"""
        table = Table(title="📋 需求分析结果", show_lines=True)
        table.add_column("模块", style="cyan", width=20)
        table.add_column("需求数", justify="center", style="green")
        table.add_column("P0", justify="center", style="red")
        table.add_column("P1", justify="center", style="yellow")
        table.add_column("P2", justify="center")
        table.add_column("P3", justify="center", style="dim")

        modules = {}
        for req in self.requirements:
            if req.module not in modules:
                modules[req.module] = {"total": 0, "P0": 0, "P1": 0, "P2": 0, "P3": 0}
            modules[req.module]["total"] += 1
            p = req.priority.upper()
            if p in modules[req.module]:
                modules[req.module][p] += 1

        for mod, stats in modules.items():
            table.add_row(
                mod,
                str(stats["total"]),
                str(stats["P0"]),
                str(stats["P1"]),
                str(stats["P2"]),
                str(stats["P3"]),
            )

        console.print(table)
        console.print(f"\n  共提取 [bold]{len(self.requirements)}[/bold] 条需求\n")

    def _show_testcases_summary(self):
        """显示测试用例摘要"""
        table = Table(title="📝 测试用例概览（前10条）", show_lines=True)
        table.add_column("序号", width=6, justify="center")
        table.add_column("用例编号", width=15)
        table.add_column("模块", width=12)
        table.add_column("优先级", width=6, justify="center")
        table.add_column("用例标题", width=40)

        for case in self.test_cases[:10]:
            priority_style = {
                "P0": "[bold red]",
                "P1": "[bold yellow]",
                "P2": "[green]",
                "P3": "[dim]",
            }.get(case.优先级, "")
            table.add_row(
                str(case.序号),
                case.用例编号,
                case.模块,
                f"{priority_style}{case.优先级}[/]",
                case.用例标题[:40],
            )

        if len(self.test_cases) > 10:
            table.add_row("...", "...", "...", "...", f"(还有 {len(self.test_cases) - 10} 条)")

        console.print(table)
        console.print(f"\n  共生成 [bold]{len(self.test_cases)}[/bold] 条测试用例\n")

    def _show_final_summary(self, result: Dict):
        """显示最终汇总"""
        summary_text = (
            f"📦 项目名称: {result['project_name']}\n"
            f"📋 需求数量: {result['requirements_count']} 条\n"
            f"📝 用例数量: {result['test_cases_count']} 条\n"
            f"📊 Excel文件: {result['excel_path']}\n"
            f"⏰ 完成时间: {result['timestamp']}\n"
            f"✅ 状态: {result['status']}"
        )
        console.print(Panel(summary_text, title="🏁 流程完成", style="bold green"))
