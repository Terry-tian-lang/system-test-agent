#!/usr/bin/env python3
"""发现百炼 Token Plan (cn-beijing) 可用模型"""
import sys, json, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.loader import get_config

BASE = "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
key = get_config().get("llm.api_key")

OUT = Path(__file__).parent.parent / "output" / "models_result.txt"
lines = []
def log(m=""):
    lines.append(m)
    print(m)

# 1) /models 端点
log("=== GET /models ===")
try:
    req = urllib.request.Request(
        BASE + "/models",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "probe/1.0"},
    )
    data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
    ids = sorted(m.get("id", "") for m in data.get("data", []))
    log(f"成功，共 {len(ids)} 个模型:")
    for i in ids:
        log(f"  - {i}")
    if ids:
        OUT.write_text("\n".join(lines), encoding="utf-8")
        sys.exit(0)
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", "ignore")[:400]
    log(f"HTTP {e.code}: {body}")
except Exception as e:
    log(f"失败: {str(e)[:300]}")

# 2) 逐个试候选模型名
log("")
log("=== 探测候选模型名 ===")
CANDIDATES = [
    "qwen3-max", "qwen3-max-preview", "qwen-max", "qwen-max-latest",
    "qwen-plus", "qwen-plus-latest", "qwen-turbo", "qwen-flash",
    "qwen3-coder-plus", "qwen3-coder-flash", "qwen-coder-plus",
    "qwen3-235b-a22b", "qwen3-235b-a22b-instruct-2507",
    "qwen3-32b", "qwen3-30b-a3b", "qwen3-coder-480b-a35b-instruct",
    "deepseek-v3", "deepseek-v3.1", "deepseek-v3.2", "deepseek-r1",
    "kimi-k2", "kimi-k2-instruct", "kimi-k2-turbo",
    "glm-4.6", "MiniMax-M2", "qwen3-vl-plus",
]

from openai import OpenAI
ok_models = []
for m in CANDIDATES:
    try:
        c = OpenAI(api_key=key, base_url=BASE, timeout=25)
        r = c.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5,
        )
        log(f"  [OK]   {m}")
        ok_models.append(m)
    except Exception as e:
        msg = str(e)
        tag = "AUTH/OTHER" if "Model not exist" not in msg else "no-model"
        log(f"  [{tag}] {m}: {msg[:110].replace(chr(10),' ')}")

log("")
log(f"=== 可用模型 ({len(ok_models)}): {ok_models} ===")
OUT.write_text("\n".join(lines), encoding="utf-8")
