# -*- coding: utf-8 -*-
"""
UI 自动化一键执行入口 (双环境自动切换)
========================================
用法:
  python run_ui_test.py                     # 默认: test 环境 / agent 平台
  python run_ui_test.py --env test          # 测试环境 (cas-func + pbw@163.com)
  python run_ui_test.py --env prod          # 生产环境 (cas.bosssoft.com.cn + tianyu@123.com)
  python run_ui_test.py --env prod --platform rag     # 生产环境 RAG 平台
  python run_ui_test.py --env test --platform agent   # 测试环境 Agent 平台
  python run_ui_test.py --env test --platform agent --headed   # 显示浏览器窗口

环境说明:
  test  cas-func.ibosssoft.com.cn   pbw@163.com        平台 ai-func (Agent/知识库Agent)
  prod  cas.bosssoft.com.cn         tianyu@123.com     平台 rag.bosssoft.com.cn (RAG 知识库)

配置文件: ui_test/env_config.py (可扩展平台/环境)
执行结果: pytest 输出 + output/ui_cases/screenshots/ 截图
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 环境 -> 默认测试文件映射 (可扩展)
PLATFORM_FILES = {
    "agent": "ui_test/test_agent_real.py",
    "rag": "ui_test/test_rag_real.py",
    "shujuzhili": "ui_test/test_shujuzhili_real.py",
}


def main():
    ap = argparse.ArgumentParser(description="UI 自动化一键执行 (双环境自动切换)")
    ap.add_argument("--env", default="test", choices=["test", "prod"],
                    help="运行环境: test(测试)/prod(生产), 默认 test")
    ap.add_argument("--platform", default="agent", choices=list(PLATFORM_FILES),
                    help="目标平台: agent/rag/shujuzhili, 默认 agent")
    ap.add_argument("--headed", action="store_true", help="显示浏览器窗口(调试)")
    ap.add_argument("--cases", nargs="+", default=None,
                    help="指定用例名, 如 test_ui_rag_001_home")
    args = ap.parse_args()

    test_file = PLATFORM_FILES[args.platform]
    if not (ROOT / test_file).exists():
        print(f"[!] 平台 {args.platform} 的用例文件不存在: {test_file} (未生成真实用例, 跳过)")
        sys.exit(0)

    cmd = [sys.executable, "-m", "pytest", test_file, "-v",
           "--env", args.env, "--platform", args.platform]
    if args.headed:
        cmd.append("--pw-headed")
    if args.cases:
        cmd.append("-k")
        cmd.append(" or ".join(args.cases))

    print("=" * 70)
    print(f"开始执行 UI 自动化")
    print(f"  环境  : {args.env}  (test=测试环境 / prod=生产环境)")
    print(f"  平台  : {args.platform}")
    print(f"  用例  : {test_file}")
    print("=" * 70)
    result = subprocess.run(cmd, cwd=str(ROOT))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()