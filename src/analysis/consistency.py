"""Repeat-sampling agreement and entropy, shared by both adapters."""

from __future__ import annotations

import math
from collections import Counter
from typing import Callable, Sequence


def summarize_repeats(
    samples: Sequence[str],
    extractor: Callable[[str], str | None],
) -> dict:
    """Majority-vote extracted labels and report agreement and Shannon entropy."""
    if not samples:
        raise ValueError("summarize_repeats requires at least one sample")
    labels = [extractor(sample) or "unparsed" for sample in samples]
    votes = Counter(labels)
    winner, winner_count = votes.most_common(1)[0]
    chosen = next(sample for sample, label in zip(samples, labels) if label == winner)
    n = len(samples)
    return {
        "n": n,
        "votes": dict(votes),
        "agreement": winner_count / n,
        "entropy": _entropy(votes, n),
        "chosen_text": chosen,
        "chosen_label": winner,
    }


def _entropy(votes: Counter, total: int) -> float:
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in votes.values():
        probability = count / total
        if probability > 0:
            entropy -= probability * math.log2(probability)
    return entropy
