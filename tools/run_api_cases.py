#!/usr/bin/env python3
"""后台运行 API 用例全量生成，进度写入 output/api_cases_run.log"""
import sys, time, traceback
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from core.console import console

OUT = ROOT / "output" / "api_cases_run.log"
lines = []
def log(m=""):
    stamp = datetime.now().strftime("%H:%M:%S")
    lines.append(f"[{stamp}] {m}")
    OUT.write_text("\n".join(lines), encoding="utf-8")

t0 = time.time()
log("=== API 用例全量生成开始 ===")

try:
    from api_test.api_case_generator import (
        load_interfaces_from_yaml, APITestCaseGenerator,
    )
    interfaces = load_interfaces_from_yaml(
        ROOT / "api_test" / "interfaces" / "ai_func_platform_api.yaml")
    log(f"加载接口: {len(interfaces)} 个")

    gen = APITestCaseGenerator()

    # 分批生成，记录每批进度
    all_cases = []
    counter = 1
    batch_size = 5
    for i in range(0, len(interfaces), batch_size):
        batch = interfaces[i:i + batch_size]
        tags = ", ".join(p.path for p in batch)
        log(f"批次 {i // batch_size + 1}: {tags[:150]}")
        try:
            cases = gen.generate(batch, batch_size=batch_size)
            log(f"  本批 {len(cases)} 条")
            for c in cases:
                c.序号 = counter
                counter += 1
            all_cases.extend(cases)
        except Exception as e:
            log(f"  批次失败: {str(e)[:200]}")
            continue
        log(f"  累计 {len(all_cases)} 条，耗时 {time.time()-t0:.0f}s")

    log(f"全部完成，共 {len(all_cases)} 条用例，总耗时 {time.time()-t0:.0f}s")

    if all_cases:
        excel = gen.export_excel(all_cases, None, "知识库平台-全量")
        log(f"EXCEL={excel}")
        log(f"RESULT=SUCCESS")
    else:
        log("RESULT=NO_CASES")

except Exception as e:
    log(f"失败: {e}")
    log(traceback.format_exc())
    log("RESULT=FAILED")