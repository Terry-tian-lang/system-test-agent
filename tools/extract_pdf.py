#!/usr/bin/env python3
"""提取 PDF 文本并保存，便于检查内容结构"""
import sys
from pathlib import Path

PDF = Path(r"C:\Users\Admin\Desktop\需求\需求文档RanV1.17.pdf")
OUT = Path(__file__).parent.parent / "output" / "ran_pdf_extract.txt"

lines = []

def log(m=""):
    lines.append(m)

try:
    import pdfplumber
    log("使用 pdfplumber 提取...")
    text_parts = []
    with pdfplumber.open(str(PDF)) as pdf:
        log(f"总页数: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages, 1):
            t = page.extract_text() or ""
            text_parts.append(f"===== 第 {i} 页 =====\n{t}")
    full = "\n\n".join(text_parts)
    log(f"提取总字符数: {len(full)}")
except Exception as e:
    log(f"pdfplumber 失败: {e}")
    # 降级到 pypdf
    try:
        from pypdf import PdfReader
        log("降级使用 pypdf 提取...")
        reader = PdfReader(str(PDF))
        log(f"总页数: {len(reader.pages)}")
        parts = []
        for i, page in enumerate(reader.pages, 1):
            t = page.extract_text() or ""
            parts.append(f"===== 第 {i} 页 =====\n{t}")
        full = "\n\n".join(parts)
        log(f"提取总字符数: {len(full)}")
    except Exception as e2:
        log(f"pypdf 也失败: {e2}")
        full = ""

OUT.write_text(full, encoding="utf-8")
log(f"\n已保存到: {OUT}")

with open(OUT, "a", encoding="utf-8") as f:
    f.write("\n\n===== 提取日志 =====\n" + "\n".join(lines))

print(f"提取完成，共 {len(full)} 字符 -> {OUT}")