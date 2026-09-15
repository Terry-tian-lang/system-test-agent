"""
离线模式 LLM 提供器 - 无需 API Key，基于规则生成测试用例

用途:
- 演示完整流程
- API Key 不可用时的降级方案
- 本地快速验证 Excel 输出

生成逻辑: 解析需求文档结构，按测试设计方法生成用例
"""
import re
from typing import List, Dict, Any, Tuple

from core.logger import logger
from core.requirement_analyzer import RequirementItem
from core.testcase_generator import TestCase


# 模块名 → 英文缩写
MODULE_ABBR = {
    "用户登录": "LOGIN", "登录": "LOGIN", "用户注册": "REG", "注册": "REG",
    "密码管理": "PWD", "个人信息": "PROFILE", "购物车": "CART",
    "订单": "ORDER", "支付": "PAY", "退款": "RFND",
}


def guess_module_abbr(module_name: str) -> str:
    """从模块名推断英文缩写"""
    for cn, en in MODULE_ABBR.items():
        if cn in module_name:
            return en
    # 回退：取英文单词首字母或模块名前3字符
    letters = re.findall(r'[A-Za-z]+', module_name)
    if letters:
        return "".join(w[0] for w in letters[:3]).upper()
    return module_name[:3].upper()


class OfflineRequirementAnalyzer:
    """离线需求分析器 - 基于正则解析需求文档"""

    def analyze(self, text: str) -> List[RequirementItem]:
        """解析需求文本，提取需求点"""
        logger.info("[离线模式] 基于规则解析需求文档...")
        requirements: List[RequirementItem] = []

        current_module = "未分类模块"
        # 匹配模块标题: ### 2.1 购物车模块 / ## 2.1 xxx
        module_pattern = re.compile(
            r'^#{2,4}\s*(?:[\d.]+\s*)?(.+?)$', re.MULTILINE
        )
        # 匹配需求条目: - **REQ-CART-001**: 添加商品到购物车
        req_pattern = re.compile(
            r'^\s*[-*]\s*\*\*(REQ-[\w-]+)\*\*\s*[:：]\s*(.+?)$', re.MULTILINE
        )
        # 也匹配: ## REQ-LOGIN-001: 用户登录
        req_pattern2 = re.compile(
            r'^#{2,4}\s*(REQ-[\w-]+)\s*[:：]\s*(.+?)$', re.MULTILINE
        )

        # 按行扫描以维护模块上下文
        lines = text.split("\n")
        module_re = re.compile(r'^#{2,4}\s*(?:[\d.]+\s*)?(.+?)\s*$')
        req_inline_re = re.compile(
            r'^\s*(?:[-*]\s*)?\*{0,2}(REQ-[\w-]+)\*{0,2}\s*[:：]\s*(.+?)\s*$'
        )
        body_lines: List[str] = []
        pending_req: Dict[str, str] = None

        def flush():
            nonlocal pending_req, body_lines
            if not pending_req:
                return
            body = "\n".join(body_lines).strip()
            desc_parts, criteria_parts, rules = [], [], []
            for bl in body.split("\n"):
                bl_s = bl.strip().lstrip("-* ").strip()
                if not bl_s:
                    continue
                if bl_s.startswith(("输入", "处理", "输出")):
                    desc_parts.append(bl_s)
                elif bl_s.startswith(("响应时间", "支持", "可用性", "并发")):
                    rules.append(bl_s)
                else:
                    criteria_parts.append(bl_s)

            description = " ".join(desc_parts) or body[:200]
            criteria = "; ".join(criteria_parts + rules) or "按需求描述验证功能正确性"
            priority = self._guess_priority(pending_req["title"], body)

            requirements.append(RequirementItem(
                req_id=pending_req["req_id"],
                module=current_module,
                title=pending_req["title"],
                description=description,
                priority=priority,
                acceptance_criteria=criteria,
            ))
            pending_req = None
            body_lines = []

        for line in lines:
            m = module_re.match(line)
            if m:
                title = m.group(1).strip()
                # 跳过纯需求标题行 (会被 req_inline_re 捕获)
                if not req_inline_re.match(line):
                    flush()
                    # 清理序号: "2.1 购物车模块" -> "购物车模块"
                    cleaned = re.sub(r'^[\d.]+\s*', '', title).strip()
                    if cleaned and "需求" not in cleaned and "概述" not in cleaned:
                        current_module = cleaned.replace("模块", "") + "模块" \
                            if not cleaned.endswith("模块") else cleaned
                    continue

            rm = req_inline_re.match(line)
            if rm:
                flush()
                pending_req = {"req_id": rm.group(1).strip(),
                               "title": rm.group(2).strip()}
                continue

            if pending_req is not None:
                body_lines.append(line)

        flush()

        # 若未解析到任何 REQ- 条目，退化为按标题分段
        if not requirements:
            requirements = self._fallback_parse(text)

        logger.info(f"[离线模式] 解析出 {len(requirements)} 条需求")
        return requirements

    def _guess_priority(self, title: str, body: str) -> str:
        """根据标题和正文推断优先级"""
        high_kw = ("登录", "注册", "支付", "下单", "密码", "权限", "认证")
        low_kw = ("美化", "提示语", "样式", "文案")
        text = title + body
        if any(k in text for k in low_kw):
            return "P3"
        if any(k in text for k in high_kw):
            return "P0"
        return "P1"

    def _fallback_parse(self, text: str) -> List[RequirementItem]:
        """回退解析：按 markdown 标题分段"""
        requirements = []
        sections = re.split(r'\n#{2,4}\s+', text)
        idx = 1
        module = "通用模块"
        for sec in sections:
            sec = sec.strip()
            if not sec or len(sec) < 20:
                continue
            first_line, _, rest = sec.partition("\n")
            title = re.sub(r'^[\d.]+\s*', '', first_line).strip()
            if len(title) < 2 or "概述" in title:
                continue
            requirements.append(RequirementItem(
                req_id=f"REQ-{idx:03d}",
                module=module,
                title=title[:50],
                description=rest.strip()[:300] or title,
                priority="P1",
                acceptance_criteria="按需求描述验证功能正确性",
            ))
            idx += 1
        return requirements


class OfflineTestCaseGenerator:
    """离线测试用例生成器 - 基于测试设计方法生成用例"""

    def generate(self, requirements: List[RequirementItem]) -> List[TestCase]:
        logger.info(f"[离线模式] 为 {len(requirements)} 条需求生成测试用例...")
        cases: List[TestCase] = []
        counter = 1

        for req in requirements:
            abbr = guess_module_abbr(req.module)
            req_cases = self._cases_for_requirement(req, abbr)
            for offset, (title, prio, ctype, pre, steps, expect,
                         notes) in enumerate(req_cases, 1):
                cases.append(TestCase(
                    序号=counter,
                    用例编号=f"TC-{abbr}-{offset:03d}",
                    模块=req.module,
                    优先级=prio,
                    类型=ctype,
                    用例标题=title,
                    前置条件=pre,
                    操作步骤=steps,
                    预期结果=expect,
                    实际结果="",
                    备注=notes,
                    关联需求=req.req_id,
                ))
                counter += 1

        logger.info(f"[离线模式] 共生成 {len(cases)} 条测试用例")
        return cases

    def _extract_fields(self, req: RequirementItem) -> Tuple[str, str, str]:
        """从需求描述中提取输入/处理/输出"""
        desc = req.description
        inp = self._grab(desc, "输入")
        proc = self._grab(desc, "处理")
        out = self._grab(desc, "输出")
        return inp or "合法参数", proc or "按业务规则处理", out or "返回处理结果"

    def _grab(self, text: str, label: str) -> str:
        m = re.search(rf'{label}\s*[:：]\s*([^\n]+)', text)
        return m.group(1).strip() if m else ""

    def _extract_constraints(self, req: RequirementItem) -> List[Tuple[str, int, int]]:
        """提取数值约束 (字段名, 最小值, 最大值)"""
        text = req.description + " " + req.acceptance_criteria
        found = []
        # 匹配: 用户名(4-20字符) / 密码: 8-32位 / 数量(1-99)
        for m in re.finditer(r'([\u4e00-\u9fa5A-Za-z]+)\s*[(:：]\s*[(\(]?(\d+)\s*[-~]\s*(\d+)', text):
            found.append((m.group(1), int(m.group(2)), int(m.group(3))))
        return found

    def _cases_for_requirement(self, req: RequirementItem,
                               abbr: str) -> List[Tuple]:
        """为单条需求生成用例集合（正向/反向/边界/异常）"""
        inp, proc, out = self._extract_fields(req)
        constraints = self._extract_constraints(req)
        criteria = req.acceptance_criteria
        cases = []

        # --- 1. 正向功能测试 (P0) ---
        cases.append((
            f"{req.title} - 正向场景验证",
            req.priority if req.priority in ("P0", "P1") else "P1",
            "功能测试",
            f"1. 系统正常运行\n2. 测试数据已准备\n3. {inp}",
            f"1. 进入对应功能页面\n2. 输入合法数据: {inp}\n3. 提交请求\n4. 观察系统响应",
            f"1. {proc}\n2. {out}\n3. 验收标准: {criteria}",
            "场景法-基本流",
        ))

        # --- 2. 边界值测试 (P1) ---
        if constraints:
            field, lo, hi = constraints[0]
            cases.append((
                f"{req.title} - {field}边界值验证(最小值{lo})",
                "P1", "边界值测试",
                f"1. 系统正常运行\n2. {field}可输入",
                f"1. 进入功能页面\n2. 输入 {field} = {lo} (下边界)\n"
                f"3. 提交并观察结果\n4. 再输入 {lo - 1} (下边界-1)\n"
                f"5. 再输入 {lo + 1} (下边界+1)",
                f"1. {field}={lo} 时通过校验\n2. {field}={lo - 1} 时拒绝并提示格式错误\n"
                f"3. {field}={lo + 1} 时通过校验",
                f"边界值分析-{field}下边界",
            ))
            cases.append((
                f"{req.title} - {field}边界值验证(最大值{hi})",
                "P1", "边界值测试",
                f"1. 系统正常运行\n2. {field}可输入",
                f"1. 进入功能页面\n2. 输入 {field} = {hi} (上边界)\n"
                f"3. 提交并观察结果\n4. 再输入 {hi + 1} (上边界+1)\n"
                f"5. 再输入 {hi - 1} (上边界-1)",
                f"1. {field}={hi} 时通过校验\n2. {field}={hi + 1} 时拒绝并提示超出限制\n"
                f"3. {field}={hi - 1} 时通过校验",
                f"边界值分析-{field}上边界",
            ))

        # --- 3. 异常测试 - 必填项为空 (P1) ---
        cases.append((
            f"{req.title} - 必填项为空校验",
            "P1", "异常测试",
            "1. 系统正常运行\n2. 已进入功能页面",
            f"1. 不输入任何数据\n2. 直接提交\n3. 观察提示信息",
            "1. 提交被拒绝\n2. 提示\"请填写必填项\"\n3. 不产生脏数据",
            "错误推测-空值输入",
        ))

        # --- 4. 异常测试 - 非法格式 (P2) ---
        cases.append((
            f"{req.title} - 非法数据格式校验",
            "P2", "异常测试",
            "1. 系统正常运行\n2. 已进入功能页面",
            f"1. 输入特殊字符: <script>alert(1)</script>\n"
            f"2. 输入超长字符串 (超过最大长度)\n"
            f"3. 输入 SQL 注入串: ' OR 1=1 --\n"
            f"4. 分别提交并观察结果",
            "1. 所有非法输入均被拒绝\n2. 返回明确的格式错误提示\n"
            "3. 无脚本执行、无 SQL 注入风险\n4. 系统不崩溃",
            "错误推测-非法输入/安全性",
        ))

        # --- 5. 业务规则验证 (P1) ---
        rule_lines = [l.strip().lstrip("-* ").strip()
                      for l in criteria.split(";") if l.strip()]
        if rule_lines and rule_lines[0]:
            cases.append((
                f"{req.title} - 业务规则验证",
                req.priority if req.priority in ("P0", "P1") else "P1",
                "功能测试",
                "1. 系统正常运行\n2. 满足业务规则触发条件",
                "\n".join(f"{i+1}. {r}" for i, r in enumerate(rule_lines[:3]))
                + "\n" + str(len(rule_lines[:3]) + 1) + ". 观察系统行为是否符合规则",
                "\n".join(f"{i+1}. 系统行为: {r}" for i, r in enumerate(rule_lines[:3])),
                "判定表-业务规则覆盖",
            ))

        # --- 6. 安全测试 (P2) ---
        cases.append((
            f"{req.title} - 未授权访问验证",
            "P2", "安全测试",
            "1. 系统正常运行\n2. 准备未登录/无效token会话",
            "1. 不携带token直接调用接口\n2. 携带过期token调用\n"
            "3. 携带其他用户的token调用\n4. 观察返回结果",
            "1. 未携带token返回 401\n2. 过期token返回 401\n"
            "3. 越权token返回 403\n4. 不泄露敏感数据",
            "错误推测-鉴权安全",
        ))

        # --- 7. 并发/性能相关 (P3) ---
        cases.append((
            f"{req.title} - 并发场景验证",
            "P3", "性能相关",
            "1. 系统正常运行\n2. 压测环境就绪",
            f"1. 模拟多用户同时执行该功能\n2. 观察响应时间和数据一致性",
            "1. 响应时间符合非功能需求\n2. 无数据错乱、无重复提交\n3. 系统稳定不崩溃",
            "错误推测-并发冲突",
        ))

        return cases


def offline_analyze(text: str) -> List[RequirementItem]:
    """便捷函数：离线需求分析"""
    return OfflineRequirementAnalyzer().analyze(text)


def offline_generate(requirements: List[RequirementItem]) -> List[TestCase]:
    """便捷函数：离线用例生成"""
    return OfflineTestCaseGenerator().generate(requirements)
