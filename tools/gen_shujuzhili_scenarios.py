#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 api_test/scenarios_shujuzhili.py (数据治理 /dmwh 统一GET只读探测)"""
import io, json, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = Path(r"D:\测试专用-deepseek\system-test-agent")
JS = ROOT / "output" / "rag_chunks" / "umi.5f3c50bb.js"
OUT = ROOT / "api_test" / "scenarios_shujuzhili.py"

s = JS.read_text(encoding="utf-8", errors="ignore")
raw = set()
for m in re.finditer(r'concat\(r,"(/[^"]{2,80})"\)', s):
    raw.add(m.group(1))
for m in re.finditer(r'concat\(r,"(/[^"]{1,60})"\)\.concat\(encodeURIComponent\(String\(([a-z])\)\),"([^"]{1,40})"\)', s):
    raw.add(m.group(1) + "{" + m.group(2) + "}" + m.group(3))
for m in re.finditer(r'concat\(r,"(/[^"]{1,60})"\)(.*?)(?:,|\))', s):
    p = m.group(1)
    rest = m.group(2)
    if "concat" in rest:
        parts = re.findall(r'concat\([^,]{0,40},?"([^"]{1,50})"\)', rest)
        raw.add(p + "{param}" + "".join(parts) if parts else p)
    else:
        raw.add(p)

def clean(p):
    if not p.startswith("/"):
        return False
    if any(ch in p for ch in (" ", "\n", "\t", "'", '"', "{", "}", "\\")):
        return False
    if not re.fullmatch(r"[/\w\-_.{}]+", p):
        return False
    return True

paths = sorted({p for p in raw if clean(p)})
# 去重: JS 中 base 常带尾斜杠产生重复条目 (/data_model/folder 与 /data_model/folder/)
# 统一保留无尾斜杠版本, 避免生产环境对尾斜杠路径超时/404
dedup = {}
for p in paths:
    key = p.rstrip("/") or p
    if key not in dedup or len(p) < len(dedup[key]):
        dedup[key] = p
paths = sorted(dedup)

# 排除纯前缀路径: JS 中仅作为 concat 前缀片段(后面拼 {id}/子路径), 裸路径 404 属预期
# 依据证据: /data_source 是 upload_file 前缀, /data_source/source 是 createDataSource 拼{id}前缀,
#           /data_subject 是 syncSubjectKnowledge 拼{id}前缀 —— 均非可独立调用的完整接口
PREFIX_ONLY = {"/data_source", "/data_source/source", "/data_subject"}
paths = [p for p in paths if p not in PREFIX_ONLY]
print(f"排除前缀路径后: {len(paths)} 条")

# 模块中文名
MOD = {
    "data_source": "数据源", "data_model": "数据模型", "data_subject": "数据主题",
    "data_mapping": "数据映射", "data_integration": "数据集成", "trans_plan": "加工方案",
    "task_manager": "任务管理", "common": "公共",
}
# 真实方法标注 (来自扫描): 键=路径 -> (真实方法, 说明)
REAL = {
    "/common/download_file": ("GET", "文件下载"),
    "/common/upload_file": ("POST", "文件上传"),
    "/data_integration/integration": ("PUT", "采集方案保存"),
    "/data_integration/integration/all": ("GET", "采集方案列表"),
    "/data_integration/integration/list": ("GET", "采集方案分页"),
    "/data_mapping/mapping": ("PUT", "映射保存"),
    "/data_mapping/mapping/preview": ("POST", "映射预览"),
    "/data_mapping/mappings": ("GET", "映射列表"),
    "/data_model/folder": ("PUT", "文件夹保存"),
    "/data_model/folder/all": ("GET", "文件夹列表"),
    "/data_model/model": ("PUT", "模型保存"),
    "/data_model/model/all": ("GET", "模型列表"),
    "/data_model/model/list": ("GET", "模型分页"),
    "/data_model/relation": ("PUT", "模型关系保存"),
    "/data_source/source/data_sources/all": ("GET", "数据源列表"),
    "/data_source/source/datetime/examples": ("GET", "时间表达式示例"),
    "/data_source/support/data_source_types": ("GET", "数据源类型"),
    "/data_source/support/databases_types": ("GET", "数据库类型"),
    "/data_source/support/table_fields": ("GET", "字段类型"),
    "/data_subject/subject/all": ("GET", "主题列表(注意DELETE批量删除存在)"),
    "/data_subject/subject/manager_actions/all": ("GET", "主题管理动作"),
    "/task_manager/tasks/": ("GET", "任务列表"),
    "/trans_plan/aggs/all": ("GET", "聚合类型"),
    "/trans_plan/custom_codes": ("POST", "自定义代码保存"),
    "/trans_plan/expression/check": ("POST", "表达式校验"),
    "/trans_plan/functions/all": ("GET", "加工函数"),
    "/trans_plan/plan": ("PUT", "加工方案保存"),
    "/trans_plan/plan/all": ("GET", "加工方案列表(注意DELETE批量删除存在)"),
    "/trans_plan/plan/list": ("GET", "加工方案分页(注意DELETE批量删除存在)"),
}

def title_from(p):
    seg = p.strip("/").split("/")
    last = seg[-1]
    if last in ("all", "list", "preview", "examples"):
        base = seg[-2] if len(seg) >= 2 else last
    else:
        base = last
    return base

lines = []
lines.append('# -*- coding: utf-8 -*-')
lines.append('"""')
lines.append('回归场景 - 数据治理 (shujuzhili) /dmwh 接口')
lines.append('平台: shujuzhili | 服务: dmwh | base: https://rag-runtime.bosssoft.com.cn (生产)')
lines.append('')
lines.append('!! 安全约束: 生产环境统一 GET 只读探测, 绝不执行写方法 !')
lines.append('真实方法(来自接口面: PUT/POST/DELETE) 以 desc 标注, 实际请求均 GET:')
lines.append('  - GET 读接口: 200 + code:0 = 业务正常')
lines.append('  - 写接口 GET 探测: 200/400/405 = 路由存在(方法由真实方法提供)')
lines.append('  - 404 = 路由不存在')
lines.append('生成: tools/gen_shujuzhili_scenarios.py (勿手改数据)')
lines.append('"""')
lines.append('from pathlib import Path')
lines.append('')
lines.append('THIS_DIR = Path(__file__).parent')
lines.append('')
lines.append('SCENARIOS = {')

idx = 0
cur_mod = None
for p in paths:
    mod = p.strip("/").split("/")[0]
    if mod not in MOD:
        continue
    idx += 1
    cid = f"SJZL-{idx:03d}"
    real_m, real_desc = REAL.get(p, ("?", ""))
    title = f"{MOD[mod]}-{title_from(p)}"
    if real_desc:
        title = f"{MOD[mod]}-{real_desc}"
    desc = f"路由探测(真实方法{real_m})" if real_m != "GET" else "读取列表/枚举"
    if "{" in p:
        desc += " [需真实ID, 只读探测验证路由]"
    if "subject/all" in p or "plan/all" in p or "plan/list" in p:
        desc += " [DELETE批量删除风险!! 仅GET探测]"
    step = (f'        {{"method": "GET", "path": "{p}", "expect": ["200", "400", "405"],'
            f' "desc": "{desc}"}},')
    lines.append(f'    "{cid}": {{"title": "{title}", "module": "{MOD[mod]}", "priority": "P1",'
                 f' "service": "dmwh", "steps": [')
    lines.append(step)
    lines.append('    ]},')

lines.append('}')
lines.append('')
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"已生成 {OUT.name}: {idx} 条场景")