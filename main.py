#!/usr/bin/env python3
"""
全流程系统测试Agent - 主入口程序

功能模块：
1. 需求分析 → 结构化需求提取
2. 测试用例生成 → LLM 驱动的测试用例设计
3. Excel 导出 → 格式化测试用例文档
4. [预留] API 接口测试
5. [预留] UI 自动化测试
6. [预留] 性能测试
7. [预留] Bug 报告（含截图）
8. [预留] 测试报告生成
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    # 尝试设置控制台为 UTF-8
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import click
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from config.loader import get_config
from core.console import console          # 必须在其他 rich 输出前导入（会重配 UTF-8）
from core.pipeline import TestPipeline
from core.requirement_analyzer import RequirementAnalyzer
from core.testcase_generator import TestCaseGenerator
from core.excel_exporter import ExcelExporter
from core.logger import logger


def setup_file_logger(output_dir: str):
    """配置文件日志"""
    os.makedirs(output_dir, exist_ok=True)
    logger.add(
        os.path.join(output_dir, "agent_{time:YYYYMMDD}.log"),
        level="DEBUG",
    )


@click.group()
@click.version_option(version="1.0.0", prog_name="system-test-agent")
def cli():
    """🧪 全流程系统测试Agent - AI驱动的自动化测试平台"""
    pass


@cli.command()
@click.option("--source", "-s", type=str, help="需求文件路径或直接输入的需求文本")
@click.option("--output", "-o", type=str, default=None, help="Excel 输出路径")
@click.option("--project", "-p", type=str, default="系统测试项目", help="项目名称")
@click.option("--interactive", "-i", is_flag=True, default=False, help="交互模式")
@click.option("--offline", is_flag=True, default=False, help="离线模式(规则引擎，无需API Key)")
def run(source, output, project, interactive, offline):
    """🚀 执行全流程测试（需求分析 → 用例生成 → Excel导出）"""
    setup_file_logger("./output")

    pipeline = TestPipeline(offline=offline)
    pipeline.project_name = project

    if interactive or not source:
        source = _interactive_input()

    if not source:
        console.print("[red]❌ 未提供需求来源，请指定文件路径或输入需求文本[/red]")
        sys.exit(1)

    try:
        result = pipeline.run_full_pipeline(source, output)
        console.print("\n[bold green]✅ 全流程测试完成！[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]❌ 执行失败: {e}[/bold red]")
        if not offline:
            console.print("[yellow]提示: 可加 --offline 使用规则引擎离线运行[/yellow]")
        logger.exception("流程执行异常")
        sys.exit(1)


@cli.command()
@click.option("--source", "-s", type=str, required=True, help="需求文件路径或文本")
@click.option("--offline", is_flag=True, default=False, help="离线模式")
def analyze(source, offline):
    """📋 仅执行需求分析"""
    setup_file_logger("./output")

    console.print(Panel("📋 需求分析模式", style="bold blue"))

    pipeline = TestPipeline(offline=offline)
    requirements = pipeline.run_step1_requirement_analysis(source)

    console.print(f"\n✅ 提取了 [bold]{len(requirements)}[/bold] 条需求\n")
    for req in requirements:
        console.print(f"  [{req.priority}] {req.req_id}: {req.title}")
        console.print(f"       模块: {req.module}")
        console.print(f"       验收标准: {req.acceptance_criteria[:80]}...")
        console.print()


@cli.command()
@click.option("--source", "-s", type=str, required=True, help="需求文件路径或文本")
@click.option("--output", "-o", type=str, default=None, help="Excel 输出路径")
@click.option("--project", "-p", type=str, default="系统测试项目", help="项目名称")
@click.option("--offline", is_flag=True, default=False, help="离线模式")
def generate(source, output, project, offline):
    """📝 需求分析 + 测试用例生成（输出Excel）"""
    setup_file_logger("./output")

    console.print(Panel("📝 测试用例生成模式", style="bold green"))

    pipeline = TestPipeline(offline=offline)
    pipeline.project_name = project

    # Step 1: 需求分析
    requirements = pipeline.run_step1_requirement_analysis(source)

    # Step 2: 生成用例
    test_cases = pipeline.run_step2_generate_testcases(requirements)

    # Step 3: 导出 Excel
    excel_path = pipeline.run_step3_export_excel(test_cases, output)

    console.print(f"\n[bold green]✅ 测试用例已导出: {excel_path}[/bold green]")


@cli.command("api-cases")
@click.option("--interfaces", "-i", type=str, default=None,
              help="接口清单YAML路径（默认: api_test/interfaces/ai_func_dify_api.yaml）")
@click.option("--output", "-o", type=str, default=None, help="输出Excel路径")
@click.option("--project", "-p", type=str, default="知识库平台", help="项目名称")
@click.option("--limit", "-n", type=int, default=None,
              help="仅处理前N个接口（快速验证），默认全部")
def api_cases(interfaces, output, project, limit):
    """🔌 第二把LLM：接口清单 → API测试用例（Excel）"""
    setup_file_logger("./output")

    console.print(Panel(f"🔌 API 接口测试用例生成 - {project}", style="bold cyan"))

    from api_test.api_case_generator import (
        load_interfaces_from_yaml, APITestCaseGenerator,
    )

    if interfaces is None:
        interfaces = "api_test/interfaces/ai_func_dify_api.yaml"

    all_interfaces = load_interfaces_from_yaml(interfaces)
    if not all_interfaces:
        console.print(f"[red]❌ 未从 {interfaces} 加载到接口[/red]")
        sys.exit(1)

    selected = all_interfaces[:limit] if limit else all_interfaces
    console.print(f"  📋 接口清单: {len(all_interfaces)} 个，本次处理: {len(selected)} 个")

    gen = APITestCaseGenerator()
    cases = gen.generate(selected, batch_size=8)

    if not cases:
        console.print("[red]❌ 未生成任何用例，请检查LLM配置与网络[/red]")
        sys.exit(1)

    excel = gen.export_excel(cases, output, project)
    console.print(f"\n[bold green]✅ API 测试用例已导出: {excel}[/bold green]")
    console.print(f"   📝 共 {len(cases)} 条用例")
@click.option("--offline", is_flag=True, default=False, help="离线模式")
def demo(offline):
    """🎯 使用示例需求运行演示"""
    setup_file_logger("./output")

    demo_requirement = """
# 用户登录系统需求文档

## 1. 系统概述
本系统是一个Web端用户管理系统，包含用户注册、登录、密码管理、个人信息管理等功能模块。

## 2. 功能需求

### 2.1 用户登录模块
- **REQ-LOGIN-001**: 用户可以通过用户名和密码登录系统
  - 输入: 用户名(4-20字符)、密码(8-32字符)
  - 处理: 验证用户名和密码是否匹配
  - 输出: 登录成功返回token，登录失败返回错误信息
  - 连续5次登录失败，锁定账号30分钟
  - 密码输入错误时不提示具体是用户名还是密码错误

- **REQ-LOGIN-002**: 支持"记住我"功能
  - 勾选后7天内自动登录
  - token过期后需重新登录

- **REQ-LOGIN-003**: 支持第三方登录
  - 支持微信、Google、GitHub OAuth登录
  - 首次第三方登录需绑定手机号

### 2.2 用户注册模块
- **REQ-REG-001**: 用户可以通过邮箱注册
  - 用户名: 4-20位字母数字组合，不能以数字开头
  - 邮箱: 合法邮箱格式，需验证唯一性
  - 密码: 8-32位，必须包含大小写字母和数字
  - 确认密码: 需与密码一致
  - 注册后发送验证邮件，24小时内有效

- **REQ-REG-002**: 手机号注册
  - 手机号: 11位有效手机号
  - 验证码: 6位数字，5分钟有效
  - 同一手机号60秒内不能重复发送

### 2.3 密码管理模块
- **REQ-PWD-001**: 忘记密码
  - 通过邮箱或手机号重置密码
  - 重置链接15分钟有效
  - 新密码不能与最近3次密码相同

- **REQ-PWD-002**: 修改密码
  - 需输入旧密码验证
  - 新密码需满足密码策略
  - 修改成功后所有设备强制下线

### 2.4 个人信息管理
- **REQ-PROFILE-001**: 查看和编辑个人信息
  - 可编辑: 昵称、头像、性别、生日、个人简介
  - 昵称: 2-20字符，不支持特殊字符
  - 头像: 支持jpg/png/gif，最大5MB
  - 生日: 不能大于当前日期

## 3. 非功能需求
- 登录响应时间 < 2秒
- 系统支持1000并发用户
- 密码传输使用HTTPS加密
- 所有API需要token认证(登录/注册除外)
"""

    pipeline = TestPipeline(offline=offline)
    pipeline.project_name = "用户管理系统"

    try:
        result = pipeline.run_full_pipeline(demo_requirement)
        console.print("\n[bold green]✅ 演示完成！[/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]❌ 演示失败: {e}[/bold red]")
        if not offline:
            console.print("[yellow]提示: 可加 --offline 使用规则引擎离线运行[/yellow]")
        logger.exception("演示执行异常")
        sys.exit(1)


@cli.command()
def status():
    """📊 查看项目状态和各模块进度"""
    console.print(Panel("📊 全流程测试Agent - 项目状态", style="bold cyan"))

    modules = [
        ("✅", "需求分析", "已完成", "LLM驱动的需求结构化提取"),
        ("✅", "测试用例生成", "已完成", "基于需求自动生成测试用例"),
        ("✅", "Excel导出", "已完成", "格式化测试用例Excel输出"),
        ("🔜", "API接口测试", "预留", "RESTful API自动化测试"),
        ("🔜", "UI自动化测试", "预留", "Playwright UI自动化"),
        ("🔜", "性能测试", "预留", "Locust性能压测"),
        ("🔜", "Bug报告", "预留", "含截图的缺陷报告"),
        ("🔜", "测试报告", "预留", "综合测试报告生成"),
    ]

    from rich.table import Table
    table = Table(show_lines=True)
    table.add_column("状态", width=4, justify="center")
    table.add_column("模块", width=15)
    table.add_column("进度", width=8, justify="center")
    table.add_column("说明", width=35)

    for status, name, progress, desc in modules:
        style = "green" if status == "✅" else "dim"
        table.add_row(status, name, f"[{style}]{progress}[/]", desc)

    console.print(table)


def _interactive_input() -> str:
    """交互式输入需求"""
    console.print(Panel(
        "请输入需求文档内容（支持以下输入方式）：\n"
        "1. 直接输入需求文本\n"
        "2. 输入文件路径（如: ./requirements.txt）\n\n"
        "输入 :quit 退出",
        title="📋 需求输入",
        style="bold blue"
    ))

    source = Prompt.ask("请输入需求来源")

    if source.strip().lower() == ":quit":
        sys.exit(0)

    return source


if __name__ == "__main__":
    cli()
