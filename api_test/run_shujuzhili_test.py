# -*- coding: utf-8 -*-
"""
数据治理(shujuzhili /dmwh) 一键回归入口 —— 生产环境
在 PyCharm 中打开本文件直接 Run 即可:
  - verify 模式: 全部 GET 只读探测, 验证接口路由可达性 (默认)
  - 业务回归: 附加 --mode full (仍为 GET 只读语义, 校验 code:0)
凭据从项目根目录 .env 自动读取:
  PROD_DMWH_BASE / PROD_DMWH_AUTH / PROD_DMWH_COOKIE

!! 安全: 本平台所有步骤均为 GET 只读探测, 绝不执行写方法 (生产环境) !!
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interface_auto_test import main

if __name__ == "__main__":
    # 注入 platform=shujuzhili, 保持用户附加参数(如 --mode full)
    argv = [sys.argv[0], "--platform", "shujuzhili"] + sys.argv[1:]
    sys.argv = argv
    sys.exit(main())