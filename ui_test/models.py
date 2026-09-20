# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class UICase:
    case_id: str
    platform: str
    title: str = ""
    module: str = ""
    priority: str = ""
    tag: str = "API"
    service: str = ""
    apis: List[str] = field(default_factory=list)
    ui_status: str = "pending_selector"
    steps: List[str] = field(default_factory=list)
    expect: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
