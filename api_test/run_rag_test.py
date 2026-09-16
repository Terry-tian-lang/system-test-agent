# -*- coding: utf-8 -*-
"""
知识库平台(RAG/RagFlow) 一键回归入口
在 PyCharm 中打开本文件直接 Run 即可, 无需任何参数:
  - 默认 verify 模式(免Token, 路由可达性)
  - 想跑业务回归: 附加 --mode full --token-ragflow <Key> --readonly
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interface_auto_test import main

if __name__ == "__main__":
    # 注入 platform=rag, 保持用户附加参数(如 --mode full --token-ragflow xxx)
    argv = [sys.argv[0], "--platform", "rag"] + sys.argv[1:]
    sys.argv = argv
    sys.exit(main())