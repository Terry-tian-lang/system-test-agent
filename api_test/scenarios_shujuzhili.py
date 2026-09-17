# -*- coding: utf-8 -*-
"""
回归场景 - 数据治理 (shujuzhili) /dmwh 接口
平台: shujuzhili | 服务: dmwh | base: https://rag-runtime.bosssoft.com.cn (生产)

!! 安全约束: 生产环境统一 GET 只读探测, 绝不执行写方法 !
真实方法(来自接口面: PUT/POST/DELETE) 以 desc 标注, 实际请求均 GET:
  - GET 读接口: 200 + code:0 = 业务正常
  - 写接口 GET 探测: 200/400/405 = 路由存在(方法由真实方法提供)
  - 404 = 路由不存在
生成: tools/gen_shujuzhili_scenarios.py (勿手改数据)
"""
from pathlib import Path

THIS_DIR = Path(__file__).parent

SCENARIOS = {
    "SJZL-001": {"title": "公共-文件下载", "module": "公共", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/common/download_file", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-002": {"title": "公共-文件上传", "module": "公共", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/common/upload_file", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法POST)"},
    ]},
    "SJZL-003": {"title": "数据集成-采集方案保存", "module": "数据集成", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_integration/integration", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法PUT)"},
    ]},
    "SJZL-004": {"title": "数据集成-采集方案列表", "module": "数据集成", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_integration/integration/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-005": {"title": "数据集成-采集方案分页", "module": "数据集成", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_integration/integration/list", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-006": {"title": "数据映射-映射保存", "module": "数据映射", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_mapping/mapping", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法PUT)"},
    ]},
    "SJZL-007": {"title": "数据映射-映射预览", "module": "数据映射", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_mapping/mapping/preview", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法POST)"},
    ]},
    "SJZL-008": {"title": "数据映射-映射列表", "module": "数据映射", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_mapping/mappings", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-009": {"title": "数据模型-文件夹保存", "module": "数据模型", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_model/folder", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法PUT)"},
    ]},
    "SJZL-010": {"title": "数据模型-文件夹列表", "module": "数据模型", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_model/folder/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-011": {"title": "数据模型-模型保存", "module": "数据模型", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_model/model", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法PUT)"},
    ]},
    "SJZL-012": {"title": "数据模型-模型列表", "module": "数据模型", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_model/model/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-013": {"title": "数据模型-模型分页", "module": "数据模型", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_model/model/list", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-014": {"title": "数据模型-model_folder_type", "module": "数据模型", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_model/model_folder_type/all", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-015": {"title": "数据模型-模型关系保存", "module": "数据模型", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_model/relation", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法PUT)"},
    ]},
    "SJZL-016": {"title": "数据源-data_sources", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/source/data_sources", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-017": {"title": "数据源-数据源列表", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/source/data_sources/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-018": {"title": "数据源-时间表达式示例", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/source/datetime/examples", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-019": {"title": "数据源-query", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/source/query", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-020": {"title": "数据源-remote", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/source/remote", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-021": {"title": "数据源-tables", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/source/tables", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-022": {"title": "数据源-storage_types", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/storage_types", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-023": {"title": "数据源-数据源类型", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/support/data_source_types", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-024": {"title": "数据源-数据库类型", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/support/databases_types", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-025": {"title": "数据源-字段类型", "module": "数据源", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_source/support/table_fields", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-026": {"title": "数据主题-subject", "module": "数据主题", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_subject/subject", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-027": {"title": "数据主题-主题列表(注意DELETE批量删除存在)", "module": "数据主题", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_subject/subject/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举 [DELETE批量删除风险!! 仅GET探测]"},
    ]},
    "SJZL-028": {"title": "数据主题-import", "module": "数据主题", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_subject/subject/import", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-029": {"title": "数据主题-主题管理动作", "module": "数据主题", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_subject/subject/manager_actions/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-030": {"title": "数据主题-rollback", "module": "数据主题", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/data_subject/subject/rollback", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-031": {"title": "任务管理-tasks", "module": "任务管理", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/task_manager/tasks", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-032": {"title": "加工方案-聚合类型", "module": "加工方案", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/trans_plan/aggs/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-033": {"title": "加工方案-自定义代码保存", "module": "加工方案", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/trans_plan/custom_codes", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法POST)"},
    ]},
    "SJZL-034": {"title": "加工方案-表达式校验", "module": "加工方案", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/trans_plan/expression/check", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法POST)"},
    ]},
    "SJZL-035": {"title": "加工方案-加工函数", "module": "加工方案", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/trans_plan/functions/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举"},
    ]},
    "SJZL-036": {"title": "加工方案-generate_create_sql", "module": "加工方案", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/trans_plan/join/generate_create_sql", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法?)"},
    ]},
    "SJZL-037": {"title": "加工方案-加工方案保存", "module": "加工方案", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/trans_plan/plan", "expect": ["200", "400", "405"], "desc": "路由探测(真实方法PUT)"},
    ]},
    "SJZL-038": {"title": "加工方案-加工方案列表(注意DELETE批量删除存在)", "module": "加工方案", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/trans_plan/plan/all", "expect": ["200", "400", "405"], "desc": "读取列表/枚举 [DELETE批量删除风险!! 仅GET探测]"},
    ]},
    "SJZL-039": {"title": "加工方案-加工方案分页(注意DELETE批量删除存在)", "module": "加工方案", "priority": "P1", "service": "dmwh", "steps": [
        {"method": "GET", "path": "/trans_plan/plan/list", "expect": ["200", "400", "405"], "desc": "读取列表/枚举 [DELETE批量删除风险!! 仅GET探测]"},
    ]},
}
