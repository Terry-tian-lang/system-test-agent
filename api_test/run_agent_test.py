# -*- coding: utf-8 -*-
"""
智能体平台(Agent/Dify) 一键回归入口
在 PyCharm 中打开本文件直接 Run 即可, 无需任何参数:
  - 默认 verify 模式(免Token, 路由可达性)
  - 想跑业务回归: 改下面 MODE='full' 并确保 Token 已配置(见 interface_auto_test.py 的 CONFIG)
参数说明(也可在 Run Configuration 里传):
  --mode full --token <DifyToken> --readonly
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interface_auto_test import main

if __name__ == "__main__":
    # 注入 platform=agent, 保持用户附加参数(如 --mode full --token xxx)
    argv = [sys.argv[0], "--platform", "agent"] + sys.argv[1:]
    sys.argv = argv
    sys.exit(main())