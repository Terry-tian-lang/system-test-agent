# -*- coding: utf-8 -*-
"""
知识库平台(RAG/RagFlow) 一键回归入口
在 PyCharm 中打开本文件直接 Run 即可, 无需任何参数:
  - 默认 verify 模式(免Token, 路由可达性) + 生产环境(prod, rag.bosssoft.com.cn)
  - 想跑业务回归: 附加 --mode full --token-ragflow <Key> --readonly
  - 切换环境: --env test (测试 rag-func)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interface_auto_test import main

if __name__ == "__main__":
    # 注入 platform=rag + 默认环境 prod(rag.bosssoft.com.cn), 保持用户附加参数优先
    argv = [sys.argv[0], "--platform", "rag"]
    if not any(a == "--env" or a.startswith("--env=") for a in sys.argv[1:]):
        argv += ["--env", "prod"]
    argv += sys.argv[1:]
    sys.argv = argv
    sys.exit(main())