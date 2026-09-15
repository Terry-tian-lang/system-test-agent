"""
配置加载器 - 读取 YAML 配置和环境变量
"""
import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv


class ConfigLoader:
    """统一配置管理器"""

    def __init__(self, config_path: str = None):
        # 加载 .env 文件
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        # 加载 YAML 配置
        if config_path is None:
            config_path = Path(__file__).parent / "settings.yaml"
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_yaml()

    def _load_yaml(self):
        """加载并解析 YAML 配置，支持环境变量替换"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            raw = f.read()

        # 替换 ${ENV_VAR} 格式的环境变量
        raw = self._resolve_env_vars(raw)
        self._config = yaml.safe_load(raw)

    def _resolve_env_vars(self, text: str) -> str:
        """解析文本中的环境变量引用"""
        pattern = r'\$\{([^}]+)\}'
        def replacer(match):
            var_name = match.group(1)
            value = os.environ.get(var_name, "")
            return value
        return re.sub(pattern, replacer, text)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        通过点分路径获取配置值
        例如: get("llm.api_key") -> config["llm"]["api_key"]
        """
        keys = key_path.split(".")
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def get_all(self) -> Dict[str, Any]:
        """返回完整配置字典"""
        return self._config.copy()

    def get_llm_config(self) -> Dict[str, Any]:
        """获取 LLM 配置"""
        return self.get("llm", {})

    def get_testcase_config(self) -> Dict[str, Any]:
        """获取测试用例配置"""
        return self.get("testcase", {})

    def get_excel_config(self) -> Dict[str, Any]:
        """获取 Excel 导出配置"""
        return self.get("excel", {})


# 全局配置单例
_config_instance: ConfigLoader = None


def get_config(config_path: str = None) -> ConfigLoader:
    """获取全局配置单例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance
