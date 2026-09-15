"""
PDF/文档文本提取工具

支持:
- PDF (pdfplumber 优先，pypdf 降级)
- 对提取文本做 NFKC 规范化（修复康熙部首兼容字符，如 ⽂→文、⾏→行）
- 过滤噪声行
"""
import re
import unicodedata
from pathlib import Path
from typing import List, Optional

from core.logger import logger


def normalize_cjk(text: str) -> str:
    """
    NFKC 规范化：
    - ⽂(U+2F42 康熙部首) → 文(U+6587)
    - 全角/半角统一、组合字符合并
    """
    return unicodedata.normalize("NFKC", text)


def clean_extracted_text(text: str) -> str:
    """清洗提取的文本：去空行噪声、保留有意义内容"""
    normalized = normalize_cjk(text)
    lines = []
    for line in normalized.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # 去掉纯页面装饰/孤立字符
        if len(stripped) == 1 and not stripped.isalnum():
            continue
        lines.append(stripped)
    return "\n".join(lines)


def extract_pdf_text(pdf_path: str | Path) -> str:
    """
    提取 PDF 全文文本
    :param pdf_path: PDF 文件路径
    :return: 清洗后的全文文本（带页码标记）
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    parts: List[str] = []
    total_pages = 0

    # 优先 pdfplumber（表格/文本质量好）
    try:
        import pdfplumber
        with pdfplumber.open(str(pdf_path)) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                try:
                    t = page.extract_text() or ""
                except Exception:
                    t = ""
                parts.append(f"===== 第 {i} 页 =====\n{t}")
        logger.info(f"[PDF] pdfplumber 提取 {total_pages} 页")
    except Exception as e:
        logger.warning(f"[PDF] pdfplumber 失败（{e}），降级 pypdf")
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            for i, page in enumerate(reader.pages, 1):
                try:
                    t = page.extract_text() or ""
                except Exception:
                    t = ""
                parts.append(f"===== 第 {i} 页 =====\n{t}")
            logger.info(f"[PDF] pypdf 提取 {total_pages} 页")
        except Exception as e2:
            raise RuntimeError(f"PDF 提取失败: {e2}")

    raw = "\n\n".join(parts)
    cleaned = clean_extracted_text(raw)
    logger.info(f"[PDF] 提取文本 {len(raw)} 字符 → 清洗后 {len(cleaned)} 字符")
    return cleaned


def load_document_text(path: str | Path) -> str:
    """
    统一文档加载入口：按扩展名分发
    支持: .pdf .txt .md .yaml .yml .json
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_text(path)

    if suffix in (".txt", ".md", ".yaml", ".yml", ".json", ".docx"):
        if suffix == ".docx":
            raise ValueError(
                ".docx 暂未支持，请先转换为文本/PDF，或安装 python-docx 后扩展"
            )
        text = path.read_text(encoding="utf-8", errors="replace")
        return normalize_cjk(text)

    raise ValueError(f"不支持的文件格式: {suffix}（支持 pdf/txt/md/yaml/json）")