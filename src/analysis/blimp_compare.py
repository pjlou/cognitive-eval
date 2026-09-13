"""Convergent-validity check against published BLiMP subject-verb agreement scores."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "external" / "blimp_sva_published.json"


def load_published(path: Path | None = None) -> dict[str, Any]:
    source = path or DATA_PATH
    return json.loads(source.read_text(encoding="utf-8"))


def normalize_model_name(name: str | None) -> str:
    if not name:
        return ""
    model = str(name).strip().lower()
    if "/" in model:
        model = model.rsplit("/", 1)[1]
    return model


def compare_rankings(
    suite_scores: dict[str, float],
    published: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Spearman rank correlation between suite and published BLiMP SVA scores.

    Models present on only one side are listed as unmatched, never dropped silently
    from the report. Correlation is None when fewer than two models overlap.
    """
    table = published if published is not None else load_published()
    published_by_key: dict[str, dict[str, Any]] = {}
    for row in table.get("models") or []:
        for key in row.get("model_keys") or []:
            published_by_key[normalize_model_name(key)] = row

    matched = []
    suite_unmatched = []
    used_published: set[str] = set()
    for model, accuracy in sorted(suite_scores.items()):
        key = normalize_model_name(model)
        row = published_by_key.get(key)
        if row is None:
            suite_unmatched.append({"model": model, "suite_accuracy": accuracy, "reason": "no published BLiMP SVA score"})
            continue
        display = row.get("display_name") or key
        used_published.add(display)
        matched.append(
            {
                "model": model,
                "display_name": display,
                "suite_accuracy": accuracy,
                "blimp_accuracy": row["accuracy"],
                "source": row.get("source"),
            }
        )

    published_unmatched = []
    seen_display: set[str] = set()
    for row in table.get("models") or []:
        display = row.get("display_name")
        if display in used_published or display in seen_display:
            continue
        seen_display.add(display)
        published_unmatched.append(
            {
                "display_name": display,
                "blimp_accuracy": row.get("accuracy"),
                "source": row.get("source"),
                "reason": "not present in this evaluation log",
            }
        )

    rho = None
    if len(matched) >= 2:
        rho = spearman(
            [row["suite_accuracy"] for row in matched],
            [row["blimp_accuracy"] for row in matched],
        )
    return {
        "phenomenon": table.get("phenomenon", "subject_verb_agreement"),
        "n_matched": len(matched),
        "spearman_rho": rho,
        "matched": matched,
        "suite_unmatched": suite_unmatched,
        "published_unmatched": published_unmatched,
        "documented_gaps": table.get("unmatched_suite_models") or [],
    }


def spearman(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    ranks_left = _average_ranks(left)
    ranks_right = _average_ranks(right)
    return _pearson(ranks_left, ranks_right)


def _average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index
        while end + 1 < len(order) and values[order[end + 1]] == values[order[index]]:
            end += 1
        # Ranks are 1-based; ties share the mean rank.
        average = (index + end) / 2 + 1
        for slot in range(index, end + 1):
            ranks[order[slot]] = average
        index = end + 1
    return ranks


def _pearson(left: list[float], right: list[float]) -> float | None:
    n = len(left)
    mean_left = sum(left) / n
    mean_right = sum(right) / n
    num = sum((x - mean_left) * (y - mean_right) for x, y in zip(left, right))
    den_left = math.sqrt(sum((x - mean_left) ** 2 for x in left))
    den_right = math.sqrt(sum((y - mean_right) ** 2 for y in right))
    if den_left == 0 or den_right == 0:
        return None
    return num / (den_left * den_right)
