# 🚀 部署到 GitHub 操作指南

> 状态：**本地仓库已就绪**（git init ✅ / 密钥脱敏 ✅ / .gitignore ✅ / 首次提交 ✅）
> 你只需完成下面「第 1 步」在 GitHub 网页建仓库，再照抄「第 2 步」的命令即可。

---

## 已完成的安全处理（重要）

| 项目 | 处理 |
|---|---|
| `tests/check_*_key.py` 3 个脚本 | 硬编码密钥已改为从环境变量读取，可安全公开 |
| `output/probe_result.txt` | 密钥已掩码为 `sk-sp-xxx.xxx.xxx` |
| `.env`（含真实 LLM Key） | 已被 `.gitignore` 排除，**不会**上传 |
| `output/`（全部报告/xlsx） | 已被 `.gitignore` 排除，不占仓库 |
| 首次提交 | `800f9b6` · 61 个文件 · 9233 行 |

> ⚠️ 提醒：密钥记得在各自平台**轮换/吊销后重新生成**（本机 `.env` 里的 LLM Key 曾在本会话明文出现过）；
> 今后所有密钥只放 `.env`（本地），绝不写进代码文件。

---

## 第 1 步：在 GitHub 网页创建空仓库（1 分钟）

1. 打开 https://github.com/new （需登录你的账号）
2. 填 **Repository name**：如 `system-test-agent`
3. 可见性：**Private**（私有）或 Public（公开）按你意愿
4. **不要勾选** "Add a README" / ".gitignore" / "license"（本地已有，避免冲突）
5. 点 **Create repository**

创建完成后页面会显示类似：
```
https://github.com/<你的用户名>/system-test-agent.git
```
复制这个地址（下面命令里替换 `<你的仓库地址>`）。

---

## 第 2 步：本地关联远程并推送（复制到 PowerShell 运行）

```powershell
cd D:\测试专用-deepseek\system-test-agent

# 1) 关联远程仓库（把地址换成你自己的）
git remote add origin https://github.com/<你的用户名>/system-test-agent.git

# 2) 分支改名为 main（GitHub 默认主分支名）
git branch -M main

# 3) 推送（首次会弹出 GitHub 登录窗口，按提示登录即可）
git push -u origin main
```

> 首次推送 HTTPS 会要求登录：
> - 若弹浏览器窗口 → 直接登录授权（Windows 凭据管理器会自动记住）
> - 若要求输密码 → **不是**你的登录密码，而是 **Personal Access Token**：
>   1. GitHub 网页 → 右上头像 → Settings → Developer settings → Personal access tokens → Tokens (classic)
>   2. Generate new token，勾选 `repo` 权限，生成后复制（只显示一次）
>   3. 用户名填你的 GitHub 用户名，密码框粘贴 token

---

## 推送成功后检查

- 打开 `https://github.com/<你的用户名>/system-test-agent` 应能看到全部代码
- `.env`、`output/`、报告文件**不在**仓库里（正常）
- 终端运行 `git status` 输出 `nothing to commit, working tree clean`

---

## 日常更新（改完代码后同步到 GitHub）

```powershell
cd D:\测试专用-deepseek\system-test-agent
git add -A
git commit -m "描述本次改动"
git push
```

---

## 可选：改用 SSH（免每次登录）

```powershell
# 1) 生成密钥（一路回车）
ssh-keygen -t ed25519 -C "你的GitHub邮箱"

# 2) 复制公钥内容
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | Set-Clipboard

# 3) GitHub 网页: Settings -> SSH and GPG keys -> New SSH key -> 粘贴 -> Save

# 4) 切换远程地址
git remote set-url origin git@github.com:<你的用户名>/system-test-agent.git
git push
```

---

## 常见问题

| 问题 | 解决 |
|---|---|
| `remote origin already exists` | `git remote set-url origin <新地址>` |
| `failed to push some refs` (远端有文件冲突) | 你建仓库时勾了 README → `git pull origin main --allow-unrelated-histories` 后重新 push |
| 提示输入密码但没弹浏览器 | 用上面 Personal Access Token 方式 |
| 想删掉远程重新来 | `git remote remove origin` |