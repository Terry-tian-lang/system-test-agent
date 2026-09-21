# -*- coding: utf-8 -*-
"""
UI 自动化 双环境配置
=====================
环境模型:
  test  测试环境  CAS=cas-func.ibosssoft.com.cn   账号 pbw@163.com      (Agent/ai-func)
  prod  生产环境  CAS=cas.bosssoft.com.cn         账号 tianyu@123.com   (RAG/rag.bosssoft.com.cn)

账号密码存放在 .env (不入库), 通过 email_key / password_key 映射读取。
运行方式:
  python -m pytest ui_test/test_agent_real.py -v --env test --platform agent
  python -m pytest ui_test/test_rag_real.py    -v --env prod --platform rag
默认: test / agent (保持与旧命令兼容)
"""
import copy

DEFAULT_ENV = "test"
DEFAULT_PLATFORM = "agent"

ENVS = {
    "test": {
        "name": "测试环境",
        "cas_login": "http://cas-func.ibosssoft.com.cn/cas/login",
        "email_key": "AGENT_UI_EMAIL",
        "password_key": "AGENT_UI_PASSWORD",
        "platforms": {
            "agent": {
                "base_url": "http://ai-func.ibosssoft.com.cn",
                # CAS 登录成功后的 service 回调地址(编码后拼进 cas_login)
                "callback": "http://ai-func.ibosssoft.com.cn/console/api/login-call-back",
                "back_url": "http://ai-func.ibosssoft.com.cn/home",
                "home_path": "/home",
                "state_file": "agent_state.json",
            },
            "rag": {
                "base_url": "http://rag-func.ibosssoft.com.cn",
                "callback": "http://rag-func.ibosssoft.com.cn/v1/user/login-call-back",
                "back_url": "http://rag-func.ibosssoft.com.cn/",
                "home_path": "/datasets",
                "state_file": "rag_state_test.json",
            },
            "shujuzhili": {
                "base_url": "http://rag-func.ibosssoft.com.cn",
                "callback": "http://rag-func.ibosssoft.com.cn/v1/user/login-call-back",
                "back_url": "http://rag-func.ibosssoft.com.cn/data-manage/model",
                "home_path": "/data-manage/model",
                "state_file": "shujuzhili_state_test.json",
            },
        },
    },
    "prod": {
        "name": "生产环境",
        "cas_login": "https://cas.bosssoft.com.cn/cas/login",
        "email_key": "RAG_UI_EMAIL",
        "password_key": "RAG_UI_PASSWORD",
        "platforms": {
            "agent": {
                "base_url": "https://ai-runtime.bosssoft.com.cn",
                "callback": "https://ai-runtime.bosssoft.com.cn/console/api/login-call-back",
                "back_url": "https://ai-runtime.bosssoft.com.cn/home",
                "home_path": "/home",
                "state_file": "agent_state_prod.json",
            },
            "rag": {
                "base_url": "https://rag.bosssoft.com.cn",
                "callback": "https://rag.bosssoft.com.cn/v1/user/login-call-back",
                "back_url": "https://rag.bosssoft.com.cn/",
                "home_path": "/datasets",
                "state_file": "rag_state_prod.json",
            },
            "shujuzhili": {
                "base_url": "https://rag-runtime.bosssoft.com.cn",
                "callback": "https://rag-runtime.bosssoft.com.cn/v1/user/login-call-back",
                "back_url": "https://rag-runtime.bosssoft.com.cn/data-manage/model",
                "home_path": "/data-manage/model",
                "state_file": "shujuzhili_state_prod.json",
            },
        },
    },
}


def get_env(env: str) -> dict:
    """返回指定环境配置(深拷贝, 避免误改)"""
    if env not in ENVS:
        raise KeyError(f"未知环境: {env}, 可用: {list(ENVS)}")
    return copy.deepcopy(ENVS[env])


def get_env_list() -> list:
    return list(ENVS)


def get_platforms(env: str) -> list:
    return list(ENVS[env]["platforms"])