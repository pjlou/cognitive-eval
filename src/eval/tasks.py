# src/eval/tasks.py
from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from src.schema.dataset_loader import load_all_test_items
from src.eval.scorers import structural_linguistic_scorer
import re

def convert_test_items_to_inspect_samples():
    """Converts local TestItem objects into Inspect Sample format."""
    items = load_all_test_items()
    samples = []
    
    for item in items:
        samples.append(
            Sample(
                input=item.prompt,
                target=str(item.gold_structure),
                id=item.id,
                metadata={
                    "module": item.module,
                    "tier": item.tier,
                    "phenomenon": item.phenomenon,
                    "language": item.language,
                    "rule_node_id": item.rule_node_id,
                    "gold_structure": item.gold_structure,
                    "source": item.source
                }
            )
        )
    return samples

def extract_final_choice(model_output: str, valid_choices=("a", "b", "c")) -> str | None:
    text = model_output.strip().lower()
    # Prefer an explicit final-answer marker (boxed, "answer is X", "answer: X")
    patterns = [
        r"\\boxed\{([abc])\}",
        r"final answer[^a-z]*(?:is)?[^a-z]*\(?([abc])\)?",
        r"answer[^a-z]*(?:is)?[^a-z]*\(?([abc])\)?",
    ]
    for pat in patterns:
        matches = re.findall(pat, text)
        if matches:
            return matches[-1]  # last match wins if the model restates itself
    # Fall back to the last standalone letter token in the whole response
    standalone = re.findall(r"(?<![a-z])([abc])(?![a-z])", text)
    return standalone[-1] if standalone else None

@task
def cognitive_eval_benchmark() -> Task:
    """Main Inspect AI Task for the 2x2 Crossed Cognitive-Eval Benchmark."""
    dataset = MemoryDataset(convert_test_items_to_inspect_samples())
    return Task(
        dataset=dataset,
        scorer=structural_linguistic_scorer()
    )