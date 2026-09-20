# -*- coding: utf-8 -*-
"""UI 用例/脚本生成器单测。"""
import os, sys, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from ui_test.case_builder import build_cases, classify
from ui_test.script_builder import render_script
class TestClassify(unittest.TestCase):
    def test_known_gap_by_expect_404(self):
        sc = {"title": "导入", "tag": "API", "note": "", "steps": [{"method": "POST", "path": "/import", "expect": ["404"]}]}
        self.assertEqual(classify(sc, has_home=True), "skip_known_gap")
    def test_empty_ui_pending(self):
        sc = {"title": "纯UI", "tag": "UI", "note": "", "steps": []}
        self.assertEqual(classify(sc, has_home=True), "pending_selector")
if __name__ == "__main__":
    unittest.main()
