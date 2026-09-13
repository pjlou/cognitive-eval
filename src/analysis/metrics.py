"""Item-level accuracy statistics for linguistic evaluation reports.

Chance baselines, bootstrap confidence intervals, and an exact McNemar test
are computed from scored items. No scipy dependency: the binomial tail uses
``math.comb``.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import Any, Iterable, Sequence


def _usable_label(choice: Any) -> bool:
    if not choice:
        return False
    return not (isinstance(choice, float) and math.isnan(choice))


def majority_baseline(choices: Sequence[str]) -> float | None:
    """Accuracy of always answering the most frequent gold letter in the slice."""
    labels = [str(choice).lower() for choice in choices if _usable_label(choice)]
    if not labels:
        return None
    counts = Counter(labels)
    return max(counts.values()) / len(labels)


def random_baseline(option_counts: Sequence[int]) -> float | None:
    """Mean chance accuracy, where each item contributes 1/k for k options."""
    ks = []
    for raw in option_counts:
        try:
            value = int(raw)
        except (TypeError, ValueError):
            continue
        if value > 0:
            ks.append(value)
    if not ks:
        return None
    return sum(1.0 / k for k in ks) / len(ks)


def bootstrap_ci(
    scores: Sequence[float],
    *,
    n_resamples: int = 2000,
    seed: int = 0,
    alpha: float = 0.05,
) -> tuple[float, float] | None:
    """Percentile bootstrap interval for the mean of item-level scores."""
    values = [float(score) for score in scores]
    if not values:
        return None
    if len(values) == 1:
        point = values[0]
        return point, point
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_resamples):
        draw = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(draw) / n)
    means.sort()
    return _percentile(means, 100 * (alpha / 2)), _percentile(means, 100 * (1 - alpha / 2))


def mcnemar_exact(natural_correct: Sequence[bool], novel_correct: Sequence[bool]) -> dict[str, float]:
    """Exact McNemar test on paired natural/novel outcomes.

    ``b`` is natural-correct and novel-incorrect; ``c`` is the reverse.
    The two-sided p-value is the binomial tail on the discordant pairs under p=0.5.
    """
    if len(natural_correct) != len(novel_correct):
        raise ValueError("McNemar requires equal-length paired outcomes")
    b = sum(left and not right for left, right in zip(natural_correct, novel_correct))
    c = sum((not left) and right for left, right in zip(natural_correct, novel_correct))
    n = b + c
    return {
        "n_pairs": float(len(natural_correct)),
        "b": float(b),
        "c": float(c),
        "n_discordant": float(n),
        "p_value": _mcnemar_p(b, c),
    }


def paired_outcomes(items: Iterable[dict[str, Any]]) -> tuple[list[bool], list[bool]]:
    """Pair scored items whose ``lexical_pair_of`` points both ways.

    Alternate prompt variants are excluded. An item is scored when ``correct``
    is a bool, or when ``status`` is pass/fail or CORRECT/INCORRECT.
    """
    by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id") or item.get("case_id") or item.get("sample_id")
        if not item_id or _is_alternate(item):
            continue
        scored = _is_correct(item)
        if scored is None:
            continue
        by_id[str(item_id)] = {**item, "id": str(item_id), "correct": scored}

    natural: list[bool] = []
    novel: list[bool] = []
    used: set[str] = set()
    for item_id, item in sorted(by_id.items()):
        if item_id in used:
            continue
        partner_id = item.get("lexical_pair_of")
        if not partner_id or str(partner_id) not in by_id:
            continue
        partner = by_id[str(partner_id)]
        if partner.get("lexical_pair_of") != item_id:
            continue
        left_cond = str(item.get("lexical_condition") or "")
        right_cond = str(partner.get("lexical_condition") or "")
        if {left_cond, right_cond} != {"natural", "novel"}:
            continue
        natural_item, novel_item = (item, partner) if left_cond == "natural" else (partner, item)
        natural.append(bool(natural_item["correct"]))
        novel.append(bool(novel_item["correct"]))
        used.add(item_id)
        used.add(str(partner_id))
    return natural, novel


def accuracy_gap(natural_correct: Sequence[bool], novel_correct: Sequence[bool]) -> float | None:
    if not natural_correct:
        return None
    natural_acc = sum(natural_correct) / len(natural_correct)
    novel_acc = sum(novel_correct) / len(novel_correct)
    return natural_acc - novel_acc


def _mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    observed = min(b, c)
    # Two-sided: outcomes at least as extreme as the smaller discordant count.
    tail = sum(_binom_pmf_half(k, n) for k in range(n + 1) if k <= observed or k >= n - observed)
    return min(1.0, tail)


def _binom_pmf_half(k: int, n: int) -> float:
    return math.comb(n, k) * (0.5 ** n)


def _percentile(ordered: Sequence[float], pct: float) -> float:
    if not ordered:
        return 0.0
    rank = (pct / 100) * (len(ordered) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]
    weight = rank - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def _is_alternate(item: dict[str, Any]) -> bool:
    variant = str(item.get("prompt_variant") or "canonical")
    item_id = str(item.get("id") or item.get("case_id") or "")
    return variant == "alternate" or item_id.endswith("-alt")


def _is_correct(item: dict[str, Any]) -> bool | None:
    if "correct" in item and isinstance(item["correct"], bool):
        return item["correct"]
    status = item.get("final_status") or item.get("status")
    if status in {"pass", "CORRECT"}:
        return True
    if status in {"fail", "INCORRECT"}:
        return False
    return None
