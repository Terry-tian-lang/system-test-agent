#!/usr/bin/env python3
"""探测目标系统：获取首页HTML，识别系统类型与技术栈"""
import sys, re, ssl, json
import urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TARGET = "http://ai-func.ibosssoft.com.cn/explore/apps"
OUT = ROOT / "output" / "probe_system.txt"
lines = []
def log(m=""):
    lines.append(m)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    req = urllib.request.Request(TARGET, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    resp = urllib.request.urlopen(req, timeout=30, context=ctx)
    html = resp.read().decode("utf-8", "ignore")
    log(f"状态码: {resp.status}")
    log(f"最终URL: {resp.geturl()}")
    log(f"服务器: {resp.headers.get('Server', '?')}")
    log(f"内容长度: {len(html)} 字符")
    log("")

    # Title
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
    log(f"页面标题: {m.group(1).strip() if m else '(无)'}")

    # meta 描述/关键词
    for name in ["description", "keywords", "generator"]:
        mm = re.search(
            rf'<meta[^>]+name=["\']{name}["\'][^>]+content=["\'](.*?)["\']',
            html, re.I)
        if mm:
            log(f"meta {name}: {mm.group(1).strip()[:200]}")

    # 框架识别
    idf = {
        "vue": r'id=["\']app["\']|data-v-|vue\.js|/vue/',
        "react": r'__NEXT_DATA__|react|_next/static',
        "dify": r'dify|console-api|/v1/apps|features/app',
        "fastapi/ui": r'fastapi|swagger|openapi',
        "flask": r'flask',
        "django": r'csrfmiddlewaretoken|django',
        "spring": r'Spring|XSRF-TOKEN|/api/',
    }
    low = html.lower()
    log("技术栈线索:")
    for name, pat in idf.items():
        if re.search(pat, low, re.I):
            log(f"  + {name}: 命中")

    # 引用的 JS/CSS（可能是单页应用入口）
    log("")
    log("=== 引用的资源(前20个) ===")
    assets = re.findall(r'(?:src|href)=["\']([^"\']+\.(?:js|css|json|map))["\']', html)
    assets = list(dict.fromkeys(a for a in assets if not a.startswith("data:")))[:20]
    log(f"共 {len(assets)} 个资源:")
    for a in assets:
        log(f"  {a}")

    # 内嵌 JSON 数据(Next.js/Nuxt SSR)
    log("")
    log("=== 内嵌 JSON/脚本数据检测 ===")
    for pat in [r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\})',
                r'__NEXT_DATA__\s*=\s*(\{.*?\});',
                r'window\.__NUXT__\s*=\s*(\{.*?\})']:
        mm = re.search(pat, html, re.S)
        if mm:
            raw = mm.group(1)
            log(f"  发现状态数据, 长度={len(raw)}")
            try:
                data = json.loads(raw)
                log(f"  JSON keys: {list(data.keys())[:20]}")
            except Exception as e:
                log(f"  JSON解析失败: {e}")

    # 保存原始 HTML
    html_path = ROOT / "output" / "system_home.html"
    html_path.write_text(html, encoding="utf-8")
    log(f"\nHTML 已保存: {html_path}")

except urllib.error.HTTPError as e:
    log(f"HTTP {e.code}: {e.reason}")
    body = e.read().decode("utf-8", "ignore")[:2000]
    log(f"响应体: {body[:1000]}")
except Exception as e:
    log(f"访问失败: {e}")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))