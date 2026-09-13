# src/eval/tasks.py
import os

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from src.schema.dataset_loader import load_all_test_items
from src.schema.prompt_variants import expand_prompt_variants
from src.eval.consistency import build_solver
from src.eval.scorers import structural_linguistic_scorer

def convert_test_items_to_inspect_samples(prompt_variant: str | None = None):
    """Converts local TestItem objects into Inspect Sample format."""
    items = expand_prompt_variants(load_all_test_items(), prompt_variant)
    samples = []

    for item in items:
        variant = "alternate" if str(item.id).endswith("-alt") else "canonical"
        samples.append(
            Sample(
                input=item.prompt,
                target=str(item.gold_structure),
                id=item.id,
                metadata={
                    "lexical_condition": item.lexical_condition,
                    "tier": item.tier,
                    "phenomenon": item.phenomenon,
                    "language": item.language,
                    "rule_node_id": item.rule_node_id,
                    "gold_structure": item.gold_structure,
                    "source": item.source,
                    "lexical_pair_of": item.lexical_pair_of,
                    "prompt_variant": variant,
                    "n_options": (item.gold_structure or {}).get("n_options"),
                    "correct_choice": (item.gold_structure or {}).get("correct_choice"),
                    "judge_rubric": item.judge_rubric,
                }
            )
        )
    return samples

@task
def cognitive_eval_benchmark() -> Task:
    """Main Inspect AI Task for the Tier x Lexical-condition benchmark."""
    dataset = MemoryDataset(convert_test_items_to_inspect_samples())
    repeats = int(os.getenv("EVAL_CONSISTENCY_REPEATS", "1"))
    task_kwargs = {"dataset": dataset, "scorer": structural_linguistic_scorer()}
    if repeats > 1:
        task_kwargs["solver"] = build_solver()
    return Task(**task_kwargs)