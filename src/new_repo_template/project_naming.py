from __future__ import annotations

import re


_NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")


def normalize_project_name(raw_name: str) -> str:
    normalized = _NON_ALNUM_PATTERN.sub("-", raw_name.strip().lower()).strip("-")
    if not normalized:
        raise ValueError("Project name must include at least one letter or number.")
    return normalized
