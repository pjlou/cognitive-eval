"""One alternate framing of each forced-choice prompt.

The rewrite changes the question frame and the response instruction, not the
sentence or the option contents. Stored ``alternate_prompt`` values are the
source of truth; this builder is the documented rule used to author them.
"""

from __future__ import annotations

import os
from typing import Iterable

from src.schema.test_item import TestItem

_REWRITES = (
    (
        "Respond with only the letter, no explanation.",
        "Reply with the letter alone.",
    ),
    (
        "Complete the English sentence",
        "Which verb form correctly completes",
    ),
    (
        "Complete the sentence",
        "Which verb form correctly completes",
    ),
    (
        "Read the English sentence:",
        "What follows from this sentence:",
    ),
    (
        "Read the sentence:",
        "What follows from this sentence:",
    ),
    (
        "Which sentence is acceptable in English?",
        "Which of these would a speaker of English accept?",
    ),
    (
        "What is the speaker most likely communicating?",
        "Which reading is the pragmatic message of this utterance?",
    ),
    (
        "Which reading does the continuation force?",
        "Given the continuation, which scope relation is required?",
    ),
    (
        "Explain whether this most naturally supports",
        "In your own words, say whether the continuation requires",
    ),
)


def build_alternate_prompt(prompt: str) -> str:
    text = prompt.strip()
    for old, new in _REWRITES:
        text = text.replace(old, new)
    if text == prompt.strip():
        text = "Restated forced-choice item. " + prompt.strip()
        text = text.replace(
            "Respond with only the letter, no explanation.",
            "Return only the letter.",
        )
    return text


def expand_prompt_variants(items: Iterable[TestItem], variant: str | None = None) -> list[TestItem]:
    """Return canonical items, alternate-phrasing copies, or both.

    Alternate copies drop ``lexical_pair_of`` so they are not McNemar pairs.
    """
    selected = (variant or os.getenv("EVAL_PROMPT_VARIANT") or "canonical").strip().lower()
    if selected not in {"canonical", "alternate", "both"}:
        raise ValueError(f"Unknown prompt variant {variant!r}")
    expanded: list[TestItem] = []
    for item in items:
        if selected in {"canonical", "both"}:
            expanded.append(item)
        if selected in {"alternate", "both"}:
            expanded.append(alternate_copy(item))
    return expanded


def alternate_copy(item: TestItem) -> TestItem:
    prompt = item.alternate_prompt or build_alternate_prompt(item.prompt)
    notes = (item.notes or "").rstrip()
    suffix = " Alternate prompt phrasing of the same item; excluded from natural/novel pairing."
    return item.model_copy(
        update={
            "id": f"{item.id}-alt",
            "prompt": prompt,
            "lexical_pair_of": None,
            "minimal_pair_of": None,
            "notes": (notes + suffix).strip(),
        }
    )
