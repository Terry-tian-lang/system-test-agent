# -*- coding: utf-8 -*-
"""
智能体平台(Agent/Dify) 一键回归入口
在 PyCharm 中打开本文件直接 Run 即可, 无需任何参数:
  - 默认 verify 模式(免Token, 路由可达性) + 测试环境(test, ai-func)
  - 想跑业务回归: 附加 --mode full --token <DifyToken> --readonly
  - 切换环境: --env test|prod
参数说明(也可在 Run Configuration 里传):
  --mode full --token <DifyToken> --readonly
  --env prod
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interface_auto_test import main

if __name__ == "__main__":
    # 注入 platform=agent + 默认环境 test(ai-func), 保持用户附加参数优先
    argv = [sys.argv[0], "--platform", "agent"]
    if not any(a == "--env" or a.startswith("--env=") for a in sys.argv[1:]):
        argv += ["--env", "test"]
    argv += sys.argv[1:]
    sys.argv = argv
    sys.exit(main())