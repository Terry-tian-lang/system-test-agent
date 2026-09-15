## 第二把 LLM：API 接口测试用例生成器（已就绪 ✅）

### 快速开始

```bash
# 全量生成（100个接口，约需 25-30 分钟）
python main.py api-cases -p "知识库平台"

# 快速验证（仅前N个接口）
python main.py api-cases -n 10 -p "知识库平台"

# 指定接口清单
python main.py api-cases -i api_test/interfaces/ai_func_dify_api.yaml -o output/api_cases.xlsx
```

### 输入（接口清单）

`api_test/interfaces/ai_func_dify_api.yaml` —— 由 `tests/build_inventory.py` 从前端 JS 提取生成，101 个端点，9 个分组：

| 分组 | 数量 | 说明 |
|---|---|---|
| apps | 4 | 应用管理/探索 |
| datasets | 27 | 知识库 CRUD、文档、命中测试 |
| workspaces | 16 | 工作区、成员、模型提供商 |
| plugins | 14 | 插件安装/升级/卸载 |
| tools | 10 | 工具、MCP |
| rag_pipelines | 15 | 魔改特有：RAG 管道编排 |
| conversations | 6 | 会话/消息 |
| files | 2 | 文件预览/上传 |
| system | 7 | 功能开关、账户 |

### 输出（Excel，15 列）

`序号 | 用例编号 | 接口 | 接口名称 | HTTP方法 | 优先级 | 用例标题 | 前置条件 | 请求头 | 请求参数 | 操作步骤 | 预期结果 | 实际结果 | 备注 | 关联需求`

### 用例覆盖策略（LLM 内置）

- 正向成功流（200/201）
- 参数边界（必填缺失、类型错误、超长、越界）
- 认证（无Token/无效Token/越权 → 401/403）
- 安全（SQL注入、XSS、路径遍历、IDOR）
- 业务规则、幂等性

### 下一步

1. ⚠️ **需要有效 Token**（浏览器登录后抓 `Authorization: Bearer xxx`），填入后即可执行真实接口测试
2. 执行器（`api_test/runner.py`）—— 按用例 JSON 发送真实请求并断言
3. 与测试报告模块集成