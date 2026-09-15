"""
LLM 客户端封装 - 统一的调用入口，含 JSON 模式降级与容错

设计要点:
1. 优先使用 response_format=json_object（结构化更稳）
2. 若模型不支持则自动降级为纯 prompt 引导
3. 健壮的 JSON 清洗（markdown 围栏、前后缀噪声、截断修复）
4. 失败重试
"""
import json
import re
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

from core.logger import logger


class LLMClient:
    """统一 LLM 调用客户端"""

    def __init__(self, config=None):
        from config.loader import get_config
        self.config = config or get_config()
        cfg = self.config.get_llm_config()

        self.api_key = cfg.get("api_key", "")
        self.api_base = cfg.get("api_base", "")
        self.model = cfg.get("model", "qwen3.8-max")
        self.temperature = cfg.get("temperature", 0.3)
        self.max_tokens = cfg.get("max_tokens", 8192)
        self.timeout = cfg.get("timeout", 120)
        # 深度思考开关：关闭可大幅提速（Qwen3 系列支持）
        self.enable_thinking = cfg.get("enable_thinking", False)

        if not self.api_key:
            raise ValueError(
                "未配置 LLM_API_KEY。请编辑 .env 文件填入密钥，"
                "或使用 --offline 离线模式运行。"
            )

        self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        # 记忆该模型是否支持 json_object 模式
        self._json_mode_supported: Optional[bool] = None

    def chat(self, messages: List[Dict[str, str]],
             json_mode: bool = False,
             max_tokens: int = None,
             temperature: float = None,
             retries: int = 2) -> str:
        """
        发送对话请求，返回文本
        :param messages: 消息列表
        :param json_mode: 是否要求 JSON 输出
        :param retries: 失败重试次数
        """
        kwargs = dict(
            model=self.model,
            messages=messages,
            temperature=self.temperature if temperature is None else temperature,
            max_tokens=max_tokens or self.max_tokens,
            timeout=self.timeout,
        )

        # 关闭深度思考以提速（对不支持该参数的模型无害，失败会走降级）
        if not self.enable_thinking:
            kwargs["extra_body"] = {"enable_thinking": False}

        use_json_param = json_mode and self._json_mode_supported is not False

        last_err = None
        for attempt in range(retries + 1):
            try:
                if use_json_param:
                    kwargs["response_format"] = {"type": "json_object"}

                resp = self.client.chat.completions.create(**kwargs)
                content = (resp.choices[0].message.content or "").strip()

                if json_mode and use_json_param:
                    self._json_mode_supported = True
                return content

            except Exception as e:
                last_err = e
                msg = str(e)

                # 模型不支持 enable_thinking 参数 → 去掉后重试
                if "extra_body" in kwargs and (
                    "enable_thinking" in msg
                    or "Unexpected" in msg
                    or "InvalidParameter" in msg
                    or "unsupported" in msg.lower()
                ):
                    logger.warning(f"模型 {self.model} 不接受 enable_thinking 参数，已移除")
                    kwargs.pop("extra_body", None)
                    self.enable_thinking = True   # 不再尝试
                    continue

                # 模型不支持 response_format → 降级重试
                if use_json_param and (
                    "response_format" in msg
                    or "json_object" in msg
                    or "Expecting value" in msg
                    or "not support" in msg.lower()
                ):
                    logger.warning(f"模型 {self.model} 不支持 json_object 模式，降级为 prompt 引导")
                    self._json_mode_supported = False
                    use_json_param = False
                    kwargs.pop("response_format", None)
                    # 在 system 消息中强化 JSON 约束
                    kwargs["messages"] = self._strengthen_json_prompt(messages)
                    continue

                if attempt < retries:
                    wait = 2 ** attempt
                    logger.warning(f"LLM 调用失败({attempt+1}/{retries+1})，{wait}s 后重试: {msg[:150]}")
                    time.sleep(wait)
                    continue

                logger.error(f"LLM 调用最终失败: {msg[:300]}")
                raise

        raise last_err

    def chat_json(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """发送请求并解析为 JSON 对象"""
        content = self.chat(messages, json_mode=True, **kwargs)
        return self.parse_json(content)

    def _strengthen_json_prompt(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """降级时强化 JSON 输出约束"""
        msgs = list(messages)
        extra = "\n\n【重要】只输出纯 JSON，不要 markdown 代码块，不要任何解释文字。"
        if msgs and msgs[0].get("role") == "system":
            msgs[0] = {"role": "system", "content": msgs[0]["content"] + extra}
        else:
            msgs.insert(0, {"role": "system", "content": extra.strip()})
        return msgs

    @staticmethod
    def parse_json(content: str) -> Any:
        """健壮的 JSON 解析：清洗围栏、提取片段、修复截断"""
        if not content:
            raise ValueError("LLM 返回空内容")

        text = content.strip()

        # 1) 剥离 markdown 代码围栏
        text = re.sub(r'^```(?:json|JSON)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()

        # 2) 直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 3) 提取第一个完整的 {...} 或 [...] 片段
        for open_ch, close_ch in (('{', '}'), ('[', ']')):
            start = text.find(open_ch)
            end = text.rfind(close_ch)
            if start != -1 and end > start:
                candidate = text[start:end + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    # 4) 尝试修复被截断的 JSON（补齐括号）
                    fixed = LLMClient._repair_json(candidate)
                    if fixed is not None:
                        return fixed

        raise ValueError(f"无法解析 LLM 返回的 JSON: {text[:300]}")

    @staticmethod
    def _repair_json(text: str) -> Optional[Any]:
        """尝试修复截断的 JSON"""
        # 统计未闭合的括号
        stack = []
        in_str = False
        esc = False
        for ch in text:
            if esc:
                esc = False
                continue
            if ch == '\\':
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch in '{[':
                stack.append(ch)
            elif ch in '}]':
                if stack:
                    stack.pop()

        if not stack:
            return None

        # 若在字符串中截断，先闭合字符串
        repaired = text
        if in_str:
            repaired += '"'

        # 去掉末尾不完整的键值对（如 "key": 或 尾随逗号）
        repaired = re.sub(r',\s*$', '', repaired)
        repaired = re.sub(r'"[^"]*"\s*:\s*$', '', repaired)
        repaired = re.sub(r',\s*$', '', repaired)

        # 逆序补齐括号
        for ch in reversed(stack):
            repaired += '}' if ch == '{' else ']'

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            return None
