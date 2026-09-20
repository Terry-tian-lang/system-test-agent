# -*- coding: utf-8 -*-
"""
RAG 接口主流程回归 一键入口 (按 Excel 主流程测试用例整理)
数据来源: 知识库平台-主流程回归测试用例.xlsx (RAG-001~057)
在 PyCharm 中打开本文件直接 Run 即可, 无需任何参数:
  - 默认 verify 模式(免Token, 路由可达性)
  - 想跑真实业务回归: 附加 --mode full --token-ragflow <Key> --readonly
  - 想跑写操作(创建/删除知识库): 自行去掉 --no-readonly (注意生产环境数据!)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interface_auto_test import main

if __name__ == "__main__":
    # 注入 platform=rag_mainflow, 保持用户附加参数(如 --mode full --token-ragflow xxx)
    argv = [sys.argv[0], "--platform", "rag_mainflow"] + sys.argv[1:]
    sys.argv = argv
    sys.exit(main())