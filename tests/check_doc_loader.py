#!/usr/bin/env python3
"""验证 doc_loader 对真实 PDF 的加载与规范化"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.doc_loader import load_document_text, normalize_cjk
from core.console import console

PDF = r"C:\Users\Admin\Desktop\需求\需求文档RanV1.17.pdf"

OUT = ROOT / "output" / "doc_loader_check.txt"
lines = []

def log(m=""):
    lines.append(m)

try:
    text = load_document_text(PDF)
    log(f"提取成功，共 {len(text)} 字符")
    log("")

    # 检查是否还有康熙部首兼容字符
    import unicodedata
    weird = set()
    for ch in text:
        if '\u2E80' <= ch <= '\u2FFF':  # 部首区块
            weird.add(f"{ch}(U+{ord(ch):04X})")
    if weird:
        log(f"⚠️ 仍含康熙部首字符: {sorted(weird)[:10]}")
    else:
        log("✅ 无康熙部首字符残留，规范化成功")

    # 检查常见转换
    checks = ["需求文档", "图片", "内容", "文字", "文件", "时间", "检索", "接口", "算法", "默认"]
    char_count = 0
    for w in checks:
        n = text.count(w)
        char_count += n
        if n == 0:
            log(f"  ⚠️ 未找到关键词: {w}")
    log(f"  关键词命中合计: {char_count}")
    log("")

    # 抽样展示
    log("=== 文本抽样 (前2000字符) ===")
    log(text[:2000])

except Exception as e:
    log(f"失败: {e}")
    import traceback
    log(traceback.format_exc())

OUT.write_text("\n".join(lines), encoding="utf-8")
print("检查结果已写入:", OUT)