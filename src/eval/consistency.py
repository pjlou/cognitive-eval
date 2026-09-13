"""Optional repeat sampling for Inspect AI runs.

Set EVAL_CONSISTENCY_REPEATS above 1. Pair that with a nonzero temperature
(EVAL_TEMPERATURE, default 0.7) so the repeats are not identical greedy decodes.
"""

from __future__ import annotations

import os

from src.analysis.consistency import summarize_repeats
from src.verifiers.common import extract_final_choice


def build_solver():
    from inspect_ai.solver import generate, solver

    repeats = int(os.getenv("EVAL_CONSISTENCY_REPEATS", "1"))
    if repeats <= 1:
        return generate()

    @solver
    def repeated_generate():
        async def solve(state, generate):
            samples: list[str] = []
            for _ in range(repeats):
                state = await generate(state)
                samples.append(state.output.completion or "")
            gold = (state.metadata or {}).get("gold_structure") or {}
            n_options = int(gold.get("n_options") or state.metadata.get("n_options") or 3)
            summary = summarize_repeats(
                samples,
                lambda text: extract_final_choice(text, valid_choices=tuple("abc"[:n_options])),
            )
            state.output.completion = summary["chosen_text"]
            state.metadata["consistency"] = {
                "n": summary["n"],
                "votes": summary["votes"],
                "agreement": summary["agreement"],
                "entropy": summary["entropy"],
                "chosen_label": summary["chosen_label"],
            }
            return state

        return solve

    return repeated_generate()
