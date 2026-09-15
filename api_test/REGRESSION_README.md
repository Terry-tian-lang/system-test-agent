# 接口自动化回归测试模块

将**主流程回归测试用例 Excel**（UI 操作）映射为**接口调用链**，自动执行接口回归。

## 文件说明

| 文件 | 作用 |
|---|---|
| `regression_scenarios.py` | **场景映射表**：131 条主流程用例 → 139 个接口步骤 |
| `regression_runner.py` | **回归执行器**：发请求、判定、生成报告 |
| `interfaces/ai_func_platform_api.yaml` | 三服务接口清单（Dify + RagFlow + CAS） |

## 场景数据来源

- `智能体平台开发态-主流程回归测试用例.xlsx`（Agent-001 ~ Agent-075，75 条）
- `知识库平台-主流程回归测试用例.xlsx`（RAG-001 ~ RAG-057，57 条）
- 每条用例映射为 1~2 个真实接口调用（含方法、路径、参数、预期）

## 用法

```bash
# 1) verify 模式: 无需 Token, 验证全部接口路由/网关可达性 (~1分钟)
python api_test/regression_runner.py --mode verify

# 2) full 模式: 携带真实 Token, 执行业务回归 (发真实业务请求)
#    Dify 与 RagFlow 凭证分离: --token 给 Dify(ai-func), --token-ragflow 给 RagFlow(rag-func)
python api_test/regression_runner.py --mode full --token <DifyToken> --token-ragflow <RagFlowKey>
python api_test/regression_runner.py --mode full --token-file token.txt

# 3) 单条用例 / 按平台过滤
python api_test/regression_runner.py --mode verify --case Agent-012
python api_test/regression_runner.py --mode full --token-ragflow <Key> --prefix RAG --readonly
```

## 判定语义

| 状态码 | 含义 | verify 判定 |
|---|---|---|
| 401/403 | 路由存在、需认证 | ✅ PASS |
| 405 | 路由存在、方法待修正 | ✅ PASS |
| 503 | 路由存在、功能被禁用 | ✅ PASS |
| 200-399 | 可达 | ✅ PASS |
| 404 | **路由不存在** | ❌ FAIL（接口缺口） |
| 网络异常 | 不可达 | ❌ FAIL |

## 输出

每次运行生成到 `output/回归报告/`：
- `接口回归报告_<时间戳>.xlsx` — 用例级 + 步骤级明细（红绿着色、筛选）
- `接口回归报告_<时间戳>.md` — 摘要、失败项、已知缺口

## 当前状态

### verify 模式（无 Token，路由可达性，2026-09-15）

| 指标 | 数量 |
|---|---|
| 总用例 | 131（P0 105 / P1 26） |
| 通过 | 125 |
| 失败（接口缺口） | 2 |
| 跳过（纯UI无法接口化） | 4 |

### full 模式（真实 Token，只读安全回归，2026-09-15）

```bash
python api_test/regression_runner.py --mode full --token <TOKEN> --readonly
```

| 指标 | 数量 |
|---|---|
| 总用例 | 131 |
| ✅ 通过 | 47 |
| ❌ 失败（真实缺陷） | 2 |
| 🚫 环境禁用（503） | 10 |
| ⏭️ 跳过（写操作/纯UI） | 72 |

**发现的真实缺陷**（详见 `output/回归报告/接口回归缺陷发现_20260915.md`）：
1. **P0** `POST /console/api/datasets/{id}/hit-testing` 携带 `retrieval_model={top_k:5}` 返回 500 `'score_threshold_enabled'` —— 服务端缺省键兜底
2. **P1** `/apps/{id}/import` 与 `/apps/{id}/workflows/task/{task_id}` 路由 404（魔改版不存在）

**环境约束（BLOCKED）**：工作空间管理类接口 `workspaces*`、`api-keys` 返回 503 功能禁用（sandbox 计划配置）。

### full 模式（仅 RagFlow Key，RAG 侧真实业务回归，2026-09-15 16:40）

```bash
python api_test/regression_runner.py --mode full --token-ragflow <RagFlowKey> --prefix RAG --readonly
```

| 指标 | 数量 |
|---|---|
| 总用例 | 57 |
| ✅ 通过 | 9 |
| ❌ 失败 | 0 |
| 🚫 受限（路由存在，凭证/资源受限） | 5 |
| ⏭️ 跳过（写操作/纯UI） | 43 |

**RAG 侧路由真相（本次实测修正）**：

| 场景映射 | 实测结果 | 修正后 |
|---|---|---|
| `POST /datasets/{id}/retrieval-test` | 404 伪路由 | ✅ 真路由 `POST /api/v1/searchbots/retrieval_test`（需 `kb_id`；当前 Key 该域鉴权受限 code 102 → BLOCKED） |
| `GET /datasets/{id}` 详情 | 405（方法不允许） | ✅ 详情经 `PUT /api/v1/datasets/{id}`（code 0 返回详情） |
| `/api/v1/datasets/tags` | 405 伪路由 | ✅ 真标签接口 `/api/v1/tags`（需 `tag_base_id`） |
| `GET /documents/{doc_id}/status` | 404 伪路由 | ✅ 真路由 `GET /datasets/{id}/documents/status` |

> full 模式会发真实请求：默认建议带 `--readonly`（仅 GET/检索）；确需全量写操作回归时去掉该参数
> （将真实创建/删除应用与知识库，请注意数据清理）。

## 扩展新用例

在 `regression_scenarios.py` 的 `SCENARIOS` 字典中新增条目即可：
```python
"新用例编号": {
    "title": "标题", "module": "模块", "priority": "P0",
    "platform": "agent", "service": "dify", "tag": "API",
    "steps": [
        {"method": "GET", "path": "/console/api/xxx",
         "expect": ["401", "200"], "expect_code": 200, "desc": "说明"},
    ],
},
```