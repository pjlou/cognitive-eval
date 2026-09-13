"""Remap forced-choice option letters without changing option content."""

from __future__ import annotations

import re
from typing import Sequence

_OPTION = re.compile(
    r"\(([abc])\)\s*(.+?)(?=(?:,|\s+or)?\s*\([abc]\)|[.?!]|$)",
    re.IGNORECASE | re.DOTALL,
)
_LETTERS = "abc"


def parse_options(prompt: str) -> list[tuple[str, str]]:
    """Return ``(letter, text)`` pairs in prompt order."""
    found = []
    for match in _OPTION.finditer(prompt):
        text = " ".join(match.group(2).split()).strip(" ,;")
        found.append((match.group(1).lower(), text))
    if len(found) < 2:
        raise ValueError(f"Could not parse forced-choice options from prompt: {prompt!r}")
    return found


def format_options(options: Sequence[tuple[str, str]]) -> str:
    cleaned = [(letter, text.strip(" ,;")) for letter, text in options]
    if len(cleaned) == 2:
        left, right = cleaned
        return f"({left[0]}) {left[1]} or ({right[0]}) {right[1]}"
    head = ", ".join(f"({letter}) {text}" for letter, text in cleaned[:-1])
    letter, text = cleaned[-1]
    return f"{head}, or ({letter}) {text}"


def remap_options(prompt: str, correct_choice: str, permutation: Sequence[int]) -> tuple[str, str]:
    """Apply a permutation of option slots and return ``(prompt, new_gold_letter)``.

    ``permutation[i]`` is the old slot index that moves into new letter ``i``.
    A model that tracks content answers the new gold letter; a model that tracks
    the original letter position does not.
    """
    options = parse_options(prompt)
    if len(permutation) != len(options) or sorted(permutation) != list(range(len(options))):
        raise ValueError("permutation must be a reordering of the option slots")
    gold = correct_choice.lower()
    old_index = next(index for index, (letter, _text) in enumerate(options) if letter == gold)
    rotated_text = [options[index][1] for index in permutation]
    new_gold = _LETTERS[next(index for index, slot in enumerate(permutation) if slot == old_index)]
    relabeled = [(_LETTERS[index], text) for index, text in enumerate(rotated_text)]
    matches = list(_OPTION.finditer(prompt))
    if len(matches) != len(relabeled):
        raise ValueError("option parse did not match the prompt spans")
    rewritten = prompt[: matches[0].start()] + format_options(relabeled) + prompt[matches[-1].end() :]
    return rewritten, new_gold


def shuffle_to_letter(prompt: str, correct_choice: str, target_letter: str) -> tuple[str, str]:
    """Rotate option slots until the gold content sits on ``target_letter``."""
    options = parse_options(prompt)
    target = target_letter.lower()
    letters = [letter for letter, _text in options]
    if target not in letters:
        raise ValueError(f"target letter {target!r} is not in {letters}")
    n = len(options)
    gold = correct_choice.lower()
    old_index = letters.index(gold)
    target_index = letters.index(target)
    # New slot i receives old slot (i - shift) mod n, so gold moves to target.
    shift = (target_index - old_index) % n
    permutation = [(index - shift) % n for index in range(n)]
    return remap_options(prompt, gold, permutation)
