"""
日志工具 - 基于标准库 logging，兼容 loguru 接口
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime


class ColorFormatter(logging.Formatter):
    """终端彩色日志格式"""
    COLORS = {
        "DEBUG": "\033[36m",     # cyan
        "INFO": "\033[32m",      # green
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[35m",  # magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        time_str = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        msg = record.getMessage()
        return f"{color}{time_str}{self.RESET} | {color}{record.levelname:<8}{self.RESET} | {record.name}:{record.funcName} - {color}{msg}{self.RESET}"


class Logger:
    """兼容 loguru 接口的 Logger"""

    def __init__(self):
        self._logger = logging.getLogger("test_agent")
        self._logger.setLevel(logging.DEBUG)
        self._console_handler = None
        self._file_handler = None
        self._setup_console()

    def _setup_console(self):
        if not self._console_handler:
            self._console_handler = logging.StreamHandler(sys.stderr)
            self._console_handler.setLevel(logging.INFO)
            self._console_handler.setFormatter(ColorFormatter())
            self._logger.addHandler(self._console_handler)

    def add(self, sink, **kwargs):
        """添加文件日志 handler (兼容 loguru)"""
        if isinstance(sink, str):
            # 处理带时间占位符的路径
            sink = sink.replace("{time:YYYYMMDD}", datetime.now().strftime("%Y%m%d"))
            os.makedirs(os.path.dirname(sink) if os.path.dirname(sink) else ".", exist_ok=True)
            handler = logging.FileHandler(sink, encoding="utf-8")
            handler.setLevel(kwargs.get("level", "DEBUG"))
            handler.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s - %(message)s"
            ))
            self._logger.addHandler(handler)
            self._file_handler = handler

    def remove(self):
        """移除所有 handler (兼容 loguru)"""
        for handler in self._logger.handlers[:]:
            if handler != self._console_handler:
                self._logger.removeHandler(handler)

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args)

    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args)


# 全局 logger 实例
logger = Logger()
