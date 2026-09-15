"""
统一的 Rich Console - 解决 Windows GBK 控制台无法输出 emoji/中文的问题

关键点:
1. 把 stdout/stderr 重配为 UTF-8
2. 关闭 Rich 的 legacy_windows 渲染器（它走 Win32 Console API + GBK）
这样无需手动 chcp 65001 也能正常输出。
"""
import io
import sys

from rich.console import Console


def _reconfigure_utf8():
    """把标准输出流重配为 UTF-8，失败则包一层"""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            try:
                wrapped = io.TextIOWrapper(
                    stream.buffer, encoding="utf-8",
                    errors="replace", line_buffering=True,
                )
                setattr(sys, name, wrapped)
            except Exception:
                pass


_reconfigure_utf8()

# legacy_windows=False 是关键：避免 Rich 用 Win32 Console API 按 GBK 写字符
console = Console(legacy_windows=False, soft_wrap=False)

__all__ = ["console"]
