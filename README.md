# 🧪 全流程系统测试Agent

> AI驱动的全流程自动化测试平台，从需求分析到测试报告，一站式覆盖测试全生命周期。

## 📋 项目架构

```
system-test-agent/
├── main.py                     # 主入口程序 (CLI)
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
├── config/
│   ├── settings.yaml           # 全局配置
│   └── loader.py               # 配置加载器
├── core/                       # 核心模块
│   ├── pipeline.py             # 测试流程编排器
│   ├── requirement_analyzer.py # 需求分析模块
│   ├── testcase_generator.py   # 测试用例生成模块
│   └── excel_exporter.py       # Excel 导出模块
├── api_test/                   # API 接口测试 (预留)
├── ui_test/                    # UI 自动化测试 (预留)
├── perf_test/                  # 性能测试 (预留)
├── bug_report/                 # Bug 报告 (预留)
├── report/                     # 测试报告 (预留)
├── output/                     # 输出目录
├── templates/                  # 报告模板
└── tests/                      # 项目自身测试
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd system-test-agent
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 LLM API Key
# LLM_API_KEY=your-api-key-here
```

支持 **阿里云百炼 Token Plan** / 百炼按量计费 / DeepSeek / OpenAI / 兼容 API。

#### ⚠️ 百炼 Token Plan 用户必读

Token Plan（团队版）密钥格式为 `sk-sp-xxxx.xxxx.xxxx`，与标准密钥（`sk-` + 32位十六进制）**不通用**，
必须使用**专属 base_url**，且带地域：

```yaml
# config/settings.yaml
llm:
  provider: "bailian-tokenplan"
  api_base: "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
  model: "qwen3.8-max"
  enable_thinking: false   # 关闭深度思考，提速约 2 倍
```

> 若你的 Token Plan 在其他地域，把 `cn-beijing` 换成 `cn-hangzhou` 等。
> 用 `python tests/probe_models.py` 可列出你账号下所有可用模型。

百炼按量计费（标准 `sk-` 密钥）则用：

```yaml
  api_base: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen-plus"
```

### 3. 运行

```bash
# 全流程：需求分析 → 用例生成 → Excel导出
python main.py run -s ./samples/sample_requirements.txt -p "电商订单系统"

# 使用内置示例需求演示
python main.py demo

# 交互模式
python main.py run -i

# 仅需求分析
python main.py analyze -s ./requirements.txt

# 需求分析 + 用例生成
python main.py generate -s ./requirements.txt -o ./output/cases.xlsx

# 离线模式（规则引擎，无需 API Key）
python main.py run -s ./requirements.txt --offline

# 查看项目状态
python main.py status
```

> **Windows 终端乱码/emoji 报错？** 程序已通过 `core/console.py` 自动重配 UTF-8
> 并关闭 Rich 的 legacy Windows 渲染器，无需手动 `chcp 65001`。

> **长需求文档耗时较久**：每个模块一次 LLM 调用，约 60-90 秒。
> 建议后台运行或用 `tests/run_pipeline.py`（会实时写 `output/run_log.txt`）。

## 📊 Excel 输出格式

生成的测试用例 Excel 包含以下列：

| 列名 | 说明 |
|------|------|
| 序号 | 自动编号 |
| 用例编号 | TC-模块缩写-序号 |
| 模块 | 所属功能模块 |
| 优先级 | P0(核心) / P1(重要) / P2(一般) / P3(低) |
| 类型 | 功能测试 / 边界值测试 / 异常测试 等 |
| 用例标题 | 测试用例简述 |
| 前置条件 | 执行前需满足的条件 |
| 操作步骤 | 具体操作步骤 |
| 预期结果 | 期望的输出/行为 |
| 实际结果 | 执行时填写 |
| 备注 | 补充说明 |
| 关联需求 | 对应的需求编号 |

Excel 还包括 **测试摘要** Sheet，统计优先级分布、模块分布和类型分布。

## 🔄 全流程规划

| 步骤 | 模块 | 状态 | 说明 |
|------|------|------|------|
| 1 | 需求分析 | ✅ 已实现 | LLM 解析需求文档（支持 PDF/TXT/MD），提取结构化需求 |
| 2 | 测试用例生成 | ✅ 已实现 | 基于需求自动生成测试用例 |
| 3 | Excel 导出 | ✅ 已实现 | 格式化输出，含统计摘要 |
| 4 | **系统识别** | ✅ 已实现 | 黑盒识别目标系统 + 接口梳理（前端 JS 分析 + 多域探测） |
| 5 | **API 测试用例** | ✅ 已实现 | 第二把 LLM：接口清单 → API 测试用例 Excel |
| 6 | **接口回归** | ✅ 已实现 | 主流程用例 → 接口调用链，自动执行回归（verify/full 两模式） |
| 7 | UI 自动化测试 | ✅ 已实现 | Playwright UI 自动化 (双环境切换) |
| 8 | 性能测试 | 🔜 预留 | Locust 性能压测 |
| 9 | Bug 报告 | 🔜 预留 | 含截图的缺陷报告 |
| 10 | 测试报告 | 🔜 预留 | 综合测试报告 |

### 🎯 系统识别与接口梳理（第4步）

对目标系统做黑盒侦察，输出系统识别报告 + 接口清单：

```bash
# 探测系统首页与技术栈
python tests/probe_system.py

# 分析前端 JS 提取 API 端点
python tests/probe_js_deep.py

# 生成结构化接口清单 YAML (输出到 api_test/interfaces/)
python tests/build_inventory.py

# 验证接口真实性(探测100+端点, 区分401/405/503/404)
python tests/verify_interfaces.py
```

支持：Next.js/Vue/umi SPA 指纹识别、istio 网关探测、Bearer/CAS/API-Key 认证识别、
前端 JS chunk 静态分析提取 API 路径、接口真实性验证、多服务归并。

> 已识别架构：**Dify(ai-func) + RagFlow(rag-func) + CAS(cas-func)** 三服务组合平台，
> 111 个接口清单见 `api_test/interfaces/ai_func_platform_api.yaml`，验证报告见 `output/接口验证综合报告.md`。

### 🔌 API 测试用例生成（第5步）

```bash
python main.py api-cases -p "知识库平台"       # 全量
python main.py api-cases -n 10 -p "知识库平台" # 前10个接口快速验证
```

### 🔁 接口自动化回归（第6步）

把主流程测试用例 Excel（UI 步骤）翻译成接口调用链并自动执行，**支持双环境切换**：

```bash
# verify 模式: 无需Token, 验证131条主流程用例对应的接口路由可达性 (~1分钟)
python api_test/run_rag_test.py --mode verify                 # 默认生产环境 rag.bosssoft.com.cn
python api_test/run_agent_test.py --mode verify               # 默认测试环境 ai-func
python api_test/run_rag_test.py --mode verify --env test      # 切到测试环境 rag-func
python api_test/run_shujuzhili_test.py --mode verify          # 生产数据治理(rag-runtime)

# full 模式: 携带真实Token, 执行业务回归
#  Dify(ai-func) 用 --token; RagFlow(rag-func) 用 --token-ragflow (两域凭证分离)
python api_test/regression_runner.py --mode full --token <DifyToken> --token-ragflow <RagFlowKey>
python api_test/run_rag_test.py --mode full --env prod --readonly   # 生产 RAG 业务回归(只读)

# 单条用例 / 按平台过滤(如仅RAG侧)
python api_test/regression_runner.py --mode verify --case Agent-012
python api_test/regression_runner.py --mode full --token-ragflow <Key> --prefix RAG --readonly
```

**接口双环境模型**（`api_test/interface_auto_test.py` 顶部 `ENV_PROFILES`）：

| 环境 | Agent(Dify) | RAG(RagFlow) | 数据治理(dmwh) | 凭据键(.env) |
|------|------------|--------------|----------------|--------------|
| `test` 测试 | `http://ai-func.ibosssoft.com.cn` | `http://rag-func.ibosssoft.com.cn` | `http://rag-func.../dmwh` | RAG_DMWH_AUTH/COOKIE |
| `prod` 生产 | `https://ai-runtime.bosssoft.com.cn` | `https://rag.bosssoft.com.cn` | `https://rag-runtime.../dmwh` | RAGFLOW_TOKEN / PROD_DMWH_AUTH/COOKIE |

- 场景映射表：`api_test/regression_scenarios.py`（131 条 → 139 接口步骤）
- 执行器：`api_test/interface_auto_test.py`（支持 `--env test|prod` 自动切换）
- 报告输出：`output/回归报告/接口回归报告_<时间戳>.xlsx/.md`（含环境标识）
- 详细文档见 `api_test/REGRESSION_README.md`

> ✅ **真实回归已执行**（2026-09-15，携带有效 Token，`--readonly` 安全模式）：
> **Dify 侧**：47 通过 / 2 失败（真实缺陷）/ 10 环境禁用（503）/ 72 跳过。
> 发现 P0 缺陷：`datasets/{id}/hit-testing` 携带 `top_k` 返回 500 `'score_threshold_enabled'`；
> 以及 2 个 404 路由缺口（`import`、`workflows/task`）。
>
> **RagFlow 侧**（携带有效 RagFlow API Key，`--prefix RAG`）：57 用例 → **9 通过 / 0 失败 / 5 受限 / 43 跳过**。
> 实测纠正 4 组伪路由：检索测试真路由 `/api/v1/searchbots/retrieval_test`(需 kb_id)；
> 数据集详情经 PUT；标签接口 `/api/v1/tags`(需 tag_base_id)；解析状态 `/documents/status`。
> 详细见 `output/回归报告/接口回归缺陷发现_20260915.md`。

详细文档见 `api_test/README.md`。

## 🖥️ UI 自动化（第7步）

Playwright UI 自动化，支持 **测试/生产双环境自动切换**：

### 双环境模型

| 环境 | CAS 登录地址 | 账号 | 平台入口 |
|------|-------------|------|---------|
| `test` 测试环境 | `http://cas-func.ibosssoft.com.cn/cas/login` | pbw@163.com | ai-func (Agent) / rag-func (RAG) |
| `prod` 生产环境 | `https://cas.bosssoft.com.cn/cas/login` | tianyu@123.com | rag.bosssoft.com.cn (RAG) |

账号密码在 `.env`（不入库）：`AGENT_UI_EMAIL/PASSWORD`（test）、`RAG_UI_EMAIL/PASSWORD`（prod）。
平台/CAS 配置在 `ui_test/env_config.py`，可按需扩展。

### 一键执行（自动切换环境）

```bash
# 测试环境 Agent 平台 (默认)
python run_ui_test.py
python run_ui_test.py --env test --platform agent

# 测试环境 RAG 平台
python run_ui_test.py --env test --platform rag

# 生产环境 RAG 平台
python run_ui_test.py --env prod --platform rag

# 调试: 显示浏览器窗口 / 只跑单条用例
python run_ui_test.py --env prod --platform rag --headed
python run_ui_test.py --env prod --platform rag --cases test_ui_rag_001_home
```

等价 pytest 命令（可直接加 pytest 参数）：
```bash
python -m pytest ui_test/test_agent_real.py -v --env test --platform agent
python -m pytest ui_test/test_rag_real.py    -v --env prod --platform rag
python -m pytest ui_test/test_rag_real.py    -v --env test --platform rag
```

- 真实用例：`ui_test/test_agent_real.py`（Agent 7 条）、`ui_test/test_rag_real.py`（RAG 5 条）
- 会话按环境隔离：`output/ui_cases/agent_state.json`、`rag_state_test.json`、`rag_state_prod.json` 等，失效自动 CAS 重登
- 截图输出：`output/ui_cases/screenshots/`

> ✅ **已执行验证**：test/Agent **7/7**、test/RAG **5/5**、prod/RAG **5/5** 全部通过。

## ⚙️ 配置说明

所有配置在 `config/settings.yaml` 中管理：

- **llm**: LLM 提供商、API地址、模型、参数
- **testcase**: 用例类型、优先级分布、设计方法
- **excel**: 表头、列宽、样式
- **api_test / ui_test / perf_test**: 各测试模块配置

## 🛠 技术栈

- **Python 3.10+**
- **OpenAI SDK**: LLM 接口
- **openpyxl**: Excel 生成
- **Click**: CLI 框架
- **Rich**: 终端 UI
- **Loguru**: 日志
- **Playwright**: UI 测试 (预留)
- **Locust**: 性能测试 (预留)
