#!/usr/bin/env python3
"""执行完整测试Agent流程 - 结果写入文件（可后台运行）"""
import os, sys, time, traceback
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.console import console   # 先重配 UTF-8

OUT = ROOT / "output" / "run_log.txt"
OUT.parent.mkdir(exist_ok=True)

source = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "samples" / "sample_requirements.txt")
project = sys.argv[2] if len(sys.argv) > 2 else "电商订单系统"
mode = sys.argv[3] if len(sys.argv) > 3 else "online"

t0 = time.time()
lines = []

def log(m=""):
    stamp = datetime.now().strftime("%H:%M:%S")
    lines.append(f"[{stamp}] {m}")
    OUT.write_text("\n".join(lines), encoding="utf-8")

log(f"开始执行 | 模式={mode} | 项目={project}")
log(f"需求来源: {source}")

try:
    from core.pipeline import TestPipeline
    pipeline = TestPipeline(offline=(mode == "offline"))
    pipeline.project_name = project

    log("--- Step 1: 需求分析 ---")
    t = time.time()
    reqs = pipeline.run_step1_requirement_analysis(source)
    log(f"完成，耗时 {time.time()-t:.1f}s，提取 {len(reqs)} 条需求")
    for r in reqs:
        log(f"    [{r.priority}] {r.req_id} | {r.module} | {r.title}")

    log("--- Step 2: 生成测试用例 ---")
    t = time.time()
    cases = pipeline.run_step2_generate_testcases(reqs)
    log(f"完成，耗时 {time.time()-t:.1f}s，生成 {len(cases)} 条用例")

    # 优先级/类型分布
    from collections import Counter
    pc = Counter(c.优先级 for c in cases)
    tc = Counter(c.类型 for c in cases)
    mc = Counter(c.模块 for c in cases)
    log(f"    优先级分布: {dict(pc)}")
    log(f"    类型分布:   {dict(tc)}")
    log(f"    模块分布:   {dict(mc)}")

    log("--- Step 3: 导出 Excel ---")
    t = time.time()
    path = pipeline.run_step3_export_excel(cases)
    log(f"完成，耗时 {time.time()-t:.1f}s")
    log(f"    文件: {path}")
    if path and os.path.exists(path):
        log(f"    大小: {os.path.getsize(path)} bytes")

    log("")
    log(f"=== 全流程成功 | 总耗时 {time.time()-t0:.1f}s ===")
    log(f"RESULT=SUCCESS")
    log(f"EXCEL={path}")
    log(f"CASES={len(cases)}")

except Exception as e:
    log("")
    log(f"=== 执行失败: {e} ===")
    log(traceback.format_exc())
    log("RESULT=FAILED")
