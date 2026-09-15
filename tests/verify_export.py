#!/usr/bin/env python3
"""
验证脚本 - 确保所有核心模块正常加载和基础功能工作
"""
import os
import sys
from pathlib import Path

# 设置路径和编码
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def verify_imports():
    """验证所有模块导入"""
    print("=" * 50)
    print("[验证1] 检查模块导入...")
    print("=" * 50)

    modules = [
        ("config.loader", "配置加载器"),
        ("core.logger", "日志工具"),
        ("core.requirement_analyzer", "需求分析模块"),
        ("core.testcase_generator", "测试用例生成模块"),
        ("core.excel_exporter", "Excel导出模块"),
        ("core.pipeline", "测试流程编排器"),
    ]

    for mod_name, desc in modules:
        try:
            __import__(mod_name)
            print(f"  ✅ {desc} ({mod_name}) - 导入成功")
        except Exception as e:
            print(f"  ❌ {desc} ({mod_name}) - 导入失败: {e}")
            return False

    return True


def verify_config():
    """验证配置加载"""
    print("\n" + "=" * 50)
    print("[验证2] 检查配置加载...")
    print("=" * 50)

    from config.loader import ConfigLoader
    config = ConfigLoader()

    checks = [
        ("llm.provider", "LLM提供商"),
        ("llm.model", "LLM模型"),
        ("testcase.case_types", "用例类型"),
        ("excel.headers", "Excel表头"),
    ]

    for key, desc in checks:
        value = config.get(key)
        if value:
            print(f"  ✅ {desc}: {value}")
        else:
            print(f"  ❌ {desc}: 未配置")

    return True


def verify_excel_export():
    """验证 Excel 导出功能"""
    print("\n" + "=" * 50)
    print("[验证3] 检查 Excel 导出...")
    print("=" * 50)

    from core.testcase_generator import TestCase
    from core.excel_exporter import ExcelExporter

    # 创建模拟测试用例数据
    sample_cases = [
        TestCase(
            序号=1,
            用例编号="TC-LOGIN-001",
            模块="用户登录",
            优先级="P0",
            类型="功能测试",
            用例标题="正确用户名和密码登录成功",
            前置条件="1. 用户已注册\n2. 账号状态正常",
            操作步骤="1. 打开登录页面\n2. 输入正确用户名: testuser\n3. 输入正确密码: Test1234\n4. 点击登录按钮",
            预期结果="1. 登录成功，跳转到首页\n2. 显示用户昵称\n3. 返回有效token",
            实际结果="",
            备注="正向场景-等价类有效类",
            关联需求="REQ-LOGIN-001",
        ),
        TestCase(
            序号=2,
            用例编号="TC-LOGIN-002",
            模块="用户登录",
            优先级="P1",
            类型="异常测试",
            用例标题="错误密码登录失败",
            前置条件="1. 用户已注册",
            操作步骤="1. 打开登录页面\n2. 输入正确用户名: testuser\n3. 输入错误密码: wrong\n4. 点击登录按钮",
            预期结果="1. 登录失败\n2. 提示\"用户名或密码错误\"\n3. 不显示具体错误原因",
            实际结果="",
            备注="安全要求-模糊化错误提示",
            关联需求="REQ-LOGIN-001",
        ),
        TestCase(
            序号=3,
            用例编号="TC-LOGIN-003",
            模块="用户登录",
            优先级="P0",
            类型="边界值测试",
            用例标题="连续5次错误密码锁定账号",
            前置条件="1. 用户已注册\n2. 之前无错误记录",
            操作步骤="1. 使用错误密码连续登录5次",
            预期结果="1. 第5次后提示\"账号已锁定\"\n2. 30分钟内无法登录\n3. 30分钟后自动解锁",
            实际结果="",
            备注="边界值-恰好5次",
            关联需求="REQ-LOGIN-001",
        ),
        TestCase(
            序号=4,
            用例编号="TC-REG-001",
            模块="用户注册",
            优先级="P0",
            类型="功能测试",
            用例标题="邮箱注册-完整流程",
            前置条件="1. 邮箱未被注册",
            操作步骤="1. 打开注册页面\n2. 输入用户名: newuser\n3. 输入邮箱: new@test.com\n4. 输入密码: Abcd1234\n5. 确认密码: Abcd1234\n6. 点击注册",
            预期结果="1. 注册成功\n2. 提示\"验证邮件已发送\"\n3. 邮箱收到验证链接",
            实际结果="",
            备注="正向场景-基本流",
            关联需求="REQ-REG-001",
        ),
        TestCase(
            序号=5,
            用例编号="TC-REG-002",
            模块="用户注册",
            优先级="P1",
            类型="边界值测试",
            用例标题="用户名恰好4个字符注册成功",
            前置条件="无",
            操作步骤="1. 输入用户名: abcd (4个字符)\n2. 填写其他合法信息\n3. 提交注册",
            预期结果="注册成功",
            实际结果="",
            备注="边界值-用户名最小长度",
            关联需求="REQ-REG-001",
        ),
    ]

    # 导出
    exporter = ExcelExporter()
    output_path = os.path.join("output", "verify_test_cases.xlsx")
    os.makedirs("output", exist_ok=True)

    result = exporter.export(sample_cases, output_path, "验证测试")

    if result and os.path.exists(result):
        size = os.path.getsize(result)
        print(f"  ✅ Excel 导出成功: {result}")
        print(f"  📊 文件大小: {size} bytes")
        print(f"  📝 用例数量: {len(sample_cases)} 条")
        return True
    else:
        print(f"  ❌ Excel 导出失败")
        return False


def main():
    print("\n🧪 全流程系统测试Agent - 模块验证")
    print("=" * 50)

    results = {
        "模块导入": verify_imports(),
        "配置加载": verify_config(),
        "Excel导出": verify_excel_export(),
    }

    print("\n" + "=" * 50)
    print("📊 验证结果汇总")
    print("=" * 50)

    all_pass = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status} - {name}")
        if not passed:
            all_pass = False

    print("\n" + ("🎉 所有验证通过！" if all_pass else "⚠️ 部分验证失败，请检查"))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
