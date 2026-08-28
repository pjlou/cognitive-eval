# dashboard/utils.py
import json
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any
from inspect_ai.log import read_eval_log

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def load_eval_logs(log_dir: str | Path | None = None) -> pd.DataFrame:
    """Parses Inspect AI log files into a normalized pandas DataFrame."""
    log_path = Path(log_dir) if log_dir else PROJECT_ROOT / "eval_logs"
    records = []

    if not log_path.exists():
        return pd.DataFrame()

    # Inspect's default .eval format is binary; JSON logs remain supported.
    for file in sorted((*log_path.glob("*.eval"), *log_path.glob("*.json"))):
        data = read_eval_log(file) if file.suffix == ".eval" else json.loads(file.read_text(encoding="utf-8"))
        model_name = _get_field(_get_field(data, "eval", {}), "model", "Unknown Model")
        samples = _get_field(data, "samples", []) or []

        for sample in samples:
            scores = _get_field(sample, "scores", {}) or {}
            score_info = _get_field(scores, "structural_linguistic_scorer", {}) or {}
            metadata = _get_field(sample, "metadata", {}) or {}
            score_meta = _get_field(score_info, "metadata", {}) or {}
            score_value = _get_field(score_info, "value")
            result = score_meta.get("result") if isinstance(score_meta, dict) else None
            if result is None:
                result = "CORRECT" if score_value == 1.0 else "INCORRECT"

            records.append({
                "model": model_name,
                "sample_id": _get_field(sample, "id"),
                "module": metadata.get("module"),
                "tier": metadata.get("tier"),
                "phenomenon": metadata.get("phenomenon"),
                "language": metadata.get("language"),
                "status": result,
                "error_code": score_meta.get("error_code", "PASS"),
                "prompt": _get_field(sample, "input"),
                "raw_output": _get_field(score_info, "answer"),
                "rule_node_id": metadata.get("rule_node_id"),
                "rule_citation": score_meta.get("rule_citation"),
                "rule_explanation": score_meta.get("rule_explanation"),
                "verifier_metadata": score_meta.get("verifier_metadata", {})
            })

    return pd.DataFrame(records)

def _get_field(value: Any, field: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(field, default)
    return getattr(value, field, default)