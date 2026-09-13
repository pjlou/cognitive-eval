"""Parameter-count parsing for scaling charts."""

from __future__ import annotations

import re

_SIZE = re.compile(r"(\d+(?:\.\d+)?)\s*b\b", re.IGNORECASE)


def parameter_billions(model_name: str | None) -> float | None:
    if not model_name:
        return None
    match = _SIZE.search(str(model_name).lower())
    if not match:
        return None
    return float(match.group(1))
