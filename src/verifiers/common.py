import re

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