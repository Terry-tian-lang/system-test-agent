#!/usr/bin/env python3
"""检查 PDF 解析库可用性"""
import importlib

libraries = [
    ("pypdf", "pypdf"),
    ("PyPDF2", "PyPDF2"),
    ("pdfplumber", "pdfplumber"),
    ("fitz", "PyMuPDF"),
    ("pdfminer", "pdfminer.six"),
]

found = []
for module_name, display in libraries:
    try:
        mod = importlib.import_module(module_name)
        ver = getattr(mod, "__version__", "?")
        print(f"{display}: OK (version {ver})")
        found.append(module_name)
    except ImportError:
        print(f"{display}: MISSING")

if not found:
    print("\n需要安装 PDF 解析库: pip install pdfplumber")
else:
    print(f"\n可用: {found}")