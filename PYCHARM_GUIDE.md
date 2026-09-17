# PyCharm 运行指南：三大回归业务

> 项目根目录：`D:\测试专用-deepseek\system-test-agent`
> 三个业务全部**零第三方依赖**（只用 Python 标准库 urllib/json/ssl），无需 pip install 任何包。

---

## 一、三个业务的代码在哪

| 业务 | 一键入口脚本（Run 这个） | 场景数据文件 | 目标服务 |
|---|---|---|---|
| **① 智能体平台** | `api_test/run_agent_test.py` | `api_test/scenarios_agent.py` (74条) | Dify `http://ai-func.ibosssoft.com.cn` |
| **② 知识库平台 RAG** | `api_test/run_rag_test.py` | `api_test/scenarios_rag.py` (57条) | RagFlow `https://rag.bosssoft.com.cn` |
| **③ 数据治理 shujuzhili** | `api_test/run_shujuzhili_test.py` | `api_test/scenarios_shujuzhili.py` (39条) | 生产 `https://rag-runtime.bosssoft.com.cn/dmwh` |

公共引擎：`api_test/interface_auto_test.py`（三个入口都调用它，无需改动）
凭据文件：项目根目录 `.env`（git 已忽略，不会提交）

---

## 二、放到 PyCharm（首次配置约 2 分钟）

### 第 1 步：打开项目
```
PyCharm → File → Open → 选择 D:\测试专用-deepseek\system-test-agent → OK
```
> 注意是打开**项目根目录**，不是 api_test 子目录。

### 第 2 步：配置 Python 解释器（无需装任何包）
```
File → Settings → Project: system-test-agent → Python Interpreter
→ Add Interpreter → 选你本机的 Python 3.8+（例如 D:\python\python.exe）→ OK
```
> 不需要点 Install 任何包。若提示缺少包，忽略即可（脚本只用标准库）。

### 第 3 步：确认凭据已配置
打开项目根目录 `.env`，确认包含以下内容（键值不要删引号外的部分）：

```ini
# ① 智能体平台（Dify Token，若已过期需找管理员重新获取）
DIFY_TOKEN=

# ② 知识库平台（RagFlow API Key，当前有效）
RAGFLOW_TOKEN=ragflow-QzOGQ2...

# ③ 数据治理·生产环境（页面会话凭据）
PROD_DMWH_BASE=https://rag-runtime.bosssoft.com.cn
PROD_DMWH_AUTH=3jgC6bPJTb9rk2...
PROD_DMWH_COOKIE=session=m_UlF8fv...
```

---

## 三、运行（两种方式）

### 方式 A：右键直接 Run（推荐，最简单）
```
Project 窗口 → 展开 api_test → 右键 run_agent_test.py → Run 'run_agent_test'
```
- 三个入口分别右键运行，互不影响
- 默认 **verify 模式**（只做路由可达性探测，免 Token 也能跑）
- `run_shujuzhili_test.py` 会自动使用生产环境会话凭据

### 方式 B：Run Configuration 加参数（业务回归）
```
Run → Edit Configurations → 选中对应入口 → Parameters 填入：
```
| 业务 | 完整业务回归（推荐只读） | 说明 |
|---|---|---|
| 智能体 | `--mode full --readonly` | Token 有效时跑真实业务 |
| RAG | `--mode full --readonly` | 知识库真实接口校验 |
| shujuzhili | `--mode full` | 生产环境，GET 只读 + 业务 code 校验 |

> ⚠️ **安全提醒**：`--readonly` 是默认推荐。去掉它才会执行真实写操作
> （创建/删除应用、知识库等）。**生产环境 shujuzhili 永远不要去掉 readonly**。

---

## 四、运行结果去哪看

- 控制台：实时打印每条用例 ✅/❌/🚫 与统计
- HTML 报告（自动生成，浏览器打开）：
  `output/回归报告/接口自动化报告_YYYYMMDD_HHMMSS.html`
- 缺陷报告（已有）：`output/回归报告/数据治理_缺陷报告_404接口_20260917.md`

---

## 五、常见问题

| 问题 | 解决 |
|---|---|
| **ModuleNotFoundError: No module named 'interface_auto_test'** | 原因：没把 `api_test` 设为源根。右键 `api_test` 目录 → Mark Directory as → Sources Root（或用方式 A 右键 Run 入口脚本，不需要手动配） |
| **控制台乱码/UnicodeEncodeError** | 脚本已内置 UTF-8 输出处理；PyCharm 默认 UTF-8 无此问题。若出现，Run Configuration → 环境变量加 `PYTHONIOENCODING=utf-8` |
| **401 Unauthorized / code 109** | 凭据过期或无效。更新 `.env` 对应键值后重跑（Dify Token 曾过期过，需找管理员要新的） |
| **想跑某一条用例** | Parameters 填 `--case SJZL-014`（或 Agent-xxx / RAG-xxx） |
| **只看某个前缀** | Parameters 填 `--prefix RAG` 等 |

---

## 六、代码修改自维护

- 场景数据：三份 `scenarios_*.py` 文件顶部有结构说明，按格式加删即可
- 重新生成 shujuzhili 场景：`python tools/gen_shujuzhili_scenarios.py`
- 全量聚合（131条）：`api_test/regression_scenarios.py` 会自动合并三部分