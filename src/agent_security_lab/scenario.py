from __future__ import annotations

from pathlib import Path

import yaml

from .models import Scenario


def load_scenario(path: Path) -> Scenario:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Scenario.model_validate(raw)
