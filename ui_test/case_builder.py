# -*- coding: utf-8 -*-
"""把回归场景转成统一 UI 用例。"""
from typing import Any, Dict, List

from ui_test.models import UICase

PLATFORMS = ("agent", "rag", "shujuzhili")
SCENARIO_MODULES = {
    "agent": "api_test.scenarios_agent",
    "rag": "api_test.scenarios_rag",
    "shujuzhili": "api_test.scenarios_shujuzhili",
}


def classify(scenario: Dict[str, Any], has_home: bool) -> str:
    note = scenario.get("note") or ""
    if "已知缺口" in note:
        return "skip_known_gap"
    steps = scenario.get("steps") or []
    for step in steps:
        expect = {str(x) for x in (step.get("expect") or [])}
        if "404" in expect:
            return "skip_known_gap"
    tag = scenario.get("tag") or "API"
    if tag == "UI" and not steps:
        return "pending_selector"
    if has_home:
        return "runnable"
    return "pending_selector"


def _step_text(step: Dict[str, Any]) -> str:
    desc = (step.get("desc") or "").strip()
    method = (step.get("method") or "GET").upper()
    path = step.get("path") or ""
    if desc:
        return f"{method} {path} — {desc}"
    return f"{method} {path}"


def build_cases(platform: str, scenarios: Dict[str, Any], has_home: bool) -> List[UICase]:
    cases: List[UICase] = []
    for case_id, raw in scenarios.items():
        steps = raw.get("steps") or []
        expects: List[str] = []
        apis: List[str] = []
        step_texts: List[str] = []
        for step in steps:
            method = (step.get("method") or "GET").upper()
            path = step.get("path") or ""
            apis.append(f"{method} {path}")
            step_texts.append(_step_text(step))
            for e in step.get("expect") or []:
                expects.append(str(e))
        cases.append(UICase(
            case_id=case_id,
            platform=platform,
            title=raw.get("title") or "",
            module=raw.get("module") or "",
            priority=raw.get("priority") or "",
            tag=raw.get("tag") or "API",
            service=raw.get("service") or "",
            apis=apis,
            ui_status=classify(raw, has_home),
            steps=step_texts,
            expect=expects,
            note=raw.get("note") or "",
        ))
    return cases


def load_scenarios(platform: str) -> Dict[str, Any]:
    import importlib
    mod_name = SCENARIO_MODULES[platform]
    mod = importlib.import_module(mod_name)
    return dict(getattr(mod, "SCENARIOS") or {})
