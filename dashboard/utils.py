# dashboard/utils.py
import json
import math
from pathlib import Path
import pandas as pd
from typing import Any
from inspect_ai.log import read_eval_log

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLUSTER_POINTS_PATH = PROJECT_ROOT / "discovery_logs" / "cluster_points.json"
CLUSTER_SUMMARY_PATH = PROJECT_ROOT / "discovery_logs" / "cluster_summary.json"


def load_cluster_points() -> pd.DataFrame:
    """
    Loads Tier 2 (statistical discovery) 2D projection points for the
    dashboard scatter plot. Returns an empty DataFrame if the discovery
    pipeline hasn't been run yet, rather than raising -- mirrors how
    load_eval_logs() handles a missing eval_logs directory.
    """
    if not CLUSTER_POINTS_PATH.exists():
        return pd.DataFrame()
    with CLUSTER_POINTS_PATH.open("r", encoding="utf-8") as f:
        points = json.load(f)
    return pd.DataFrame(points)


def load_cluster_summary() -> dict[str, Any] | None:
    """Loads the Tier 2 cluster summary (sizes, distributions, example texts)."""
    if not CLUSTER_SUMMARY_PATH.exists():
        return None
    with CLUSTER_SUMMARY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_model_family(model_name: str | None) -> str:
    """Return the canonical family segment for names like 'ollama/qwen2.5:7b'."""
    if model_name is None:
        return "unknown"
    model = str(model_name).strip().lower()
    family = model.split(":", 1)[0]
    if "/" in family:
        family = family.rsplit("/", 1)[1]
    family = family.replace("qwen-2.5", "qwen2.5")
    if family == "qwen2.5" or family.startswith("qwen2.5-"):
        return "qwen2.5"
    return family


def get_model_size(model_name: str | None) -> str:
    """Return the size segment for model names like 'ollama/qwen2.5:7b'."""
    if model_name is None:
        return ""
    model = str(model_name).strip().lower()
    if ":" in model:
        return model.split(":", 1)[1]
    return ""


def get_models_for_family(df: pd.DataFrame, family: str) -> list[str]:
    """Return sorted model names belonging to a canonical family."""
    if df.empty or "model" not in df.columns:
        return []
    models = [
        str(model)
        for model in df["model"].dropna().unique()
        if get_model_family(model) == family
    ]
    return sorted(models, key=model_sort_key)


def model_sort_key(model_name: str | None) -> tuple[str, float]:
    """Sort model names by family then size for consistent chart ordering."""
    family = get_model_family(model_name)
    size = get_model_size(model_name)
    size_value = 0.0
    if size:
        size_token = size.lower().rstrip("b")
        try:
            size_value = float(size_token)
        except ValueError:
            size_value = 0.0
    return family, size_value


def build_answer_pattern_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate model response categories such as CORRECT or each failure code."""
    if df.empty:
        return pd.DataFrame(columns=["model", "family", "size", "pattern", "count", "share"])

    summary = df.copy()
    summary["pattern"] = summary["status"].where(
        summary["status"].eq("CORRECT"), summary["error_code"].fillna("UNKNOWN")
    )
    summary["family"] = summary["model"].map(get_model_family)
    summary["size"] = summary["model"].map(get_model_size)

    aggregated = (
        summary.groupby(["model", "family", "size", "pattern"], dropna=False)
        .size()
        .reset_index(name="count")
    )
    aggregated["share"] = (
        aggregated["count"] / aggregated.groupby("model")["count"].transform("sum") * 100
    )

    return aggregated.sort_values(["family", "model", "count"], ascending=[True, True, False]).reset_index(drop=True)


def _normalize_status(result: Any, score_value: Any) -> str:
    text = str(result or "").strip().upper()
    if text in {"PASS", "CORRECT"}:
        return "CORRECT"
    if text in {"FAIL", "INCORRECT"}:
        return "INCORRECT"
    return "CORRECT" if score_value == 1.0 else "INCORRECT"


def _missing(value: Any) -> bool:
    if value is None:
        return True
    return isinstance(value, float) and math.isnan(value)


def _filled(current: Any, fallback: Any) -> Any:
    return fallback if _missing(current) else current


def _as_condition(value: Any) -> str | None:
    if value is None:
        return None
    text = str(getattr(value, "value", value)).strip().lower()
    if text in {"natural", "novel"}:
        return text
    return None


def _enrich_from_dataset(records: list[dict]) -> list[dict]:
    """Fill pairing and condition from the current items when older logs omit them."""
    if not records:
        return records
    from src.schema.dataset_loader import load_all_test_items

    by_id = {item.id: item for item in load_all_test_items()}
    for row in records:
        item = by_id.get(str(row.get("sample_id") or ""))
        condition = _as_condition(row.get("lexical_condition"))
        if item is not None:
            gold = item.gold_structure or {}
            condition = condition or _as_condition(item.lexical_condition)
            row["lexical_pair_of"] = _filled(row.get("lexical_pair_of"), item.lexical_pair_of)
            row["correct_choice"] = _filled(row.get("correct_choice"), gold.get("correct_choice"))
            row["n_options"] = _filled(row.get("n_options"), gold.get("n_options"))
            if not row.get("phenomenon"):
                row["phenomenon"] = getattr(item.phenomenon, "value", item.phenomenon)
            if not row.get("tier"):
                row["tier"] = getattr(item.tier, "value", item.tier)
        row["lexical_condition"] = condition
    return records


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

            records.append({
                "model": model_name,
                "sample_id": _get_field(sample, "id"),
                "lexical_condition": metadata.get("lexical_condition"),
                "tier": metadata.get("tier"),
                "phenomenon": metadata.get("phenomenon"),
                "language": metadata.get("language"),
                "status": _normalize_status(result, score_value),
                "error_code": score_meta.get("error_code", "PASS"),
                "prompt": _get_field(sample, "input"),
                "raw_output": _get_field(score_info, "answer"),
                "rule_node_id": metadata.get("rule_node_id"),
                "rule_citation": score_meta.get("rule_citation"),
                "rule_explanation": score_meta.get("rule_explanation"),
                "verifier_metadata": score_meta.get("verifier_metadata", {}),
                "cascade_stage": score_meta.get("cascade_stage"),
                "consistency": score_meta.get("consistency"),
                "lexical_pair_of": metadata.get("lexical_pair_of"),
                "prompt_variant": metadata.get("prompt_variant", "canonical"),
                "correct_choice": metadata.get("correct_choice"),
                "n_options": metadata.get("n_options"),
            })

    return pd.DataFrame(_enrich_from_dataset(records))


def rigor_records(df: pd.DataFrame) -> list[dict]:
    """Item-level scored records, joined to the current dataset for gold letters."""
    if df.empty:
        return []
    from src.schema.dataset_loader import load_all_test_items

    by_id = {item.id: item for item in load_all_test_items()}
    records = []
    for row in df.to_dict(orient="records"):
        if str(row.get("prompt_variant") or "canonical") == "alternate":
            continue
        sample_id = str(row.get("sample_id") or "")
        item = by_id.get(sample_id)
        gold = (item.gold_structure if item else {}) or {}
        status = row.get("status")
        if status not in {"CORRECT", "INCORRECT"}:
            continue
        condition = _as_condition(row.get("lexical_condition"))
        if condition is None and item is not None:
            condition = _as_condition(item.lexical_condition)
        records.append(
            {
                "id": sample_id,
                "model": row.get("model"),
                "correct": status == "CORRECT",
                "final_status": "pass" if status == "CORRECT" else "fail",
                "correct_choice": _filled(row.get("correct_choice"), gold.get("correct_choice")),
                "n_options": _filled(row.get("n_options"), gold.get("n_options")),
                "lexical_pair_of": _filled(row.get("lexical_pair_of"), item.lexical_pair_of if item else None),
                "lexical_condition": condition,
                "prompt_variant": "canonical",
                "phenomenon": row.get("phenomenon"),
            }
        )
    return records


def scaling_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Accuracy versus parameter count, split by lexical condition and family."""
    from src.analysis.scaling import parameter_billions

    if df.empty:
        return pd.DataFrame(columns=["model", "family", "lexical_condition", "params", "accuracy"])
    frame = df.copy()
    if "prompt_variant" in frame.columns:
        frame = frame[frame["prompt_variant"].fillna("canonical") != "alternate"]
    rows = []
    for (model, condition), group in frame.groupby(["model", "lexical_condition"], dropna=False):
        params = parameter_billions(str(model))
        if params is None or not condition:
            continue
        rows.append(
            {
                "model": model,
                "family": get_model_family(str(model)),
                "lexical_condition": str(condition),
                "params": params,
                "accuracy": float((group["status"] == "CORRECT").mean()),
            }
        )
    return pd.DataFrame(rows)


def agreement_accuracy_by_model(df: pd.DataFrame) -> dict[str, float]:
    """Natural-condition agreement-attraction accuracy, the BLiMP overlap slice."""
    if df.empty:
        return {}
    frame = df[
        (df["phenomenon"] == "agreement_attraction")
        & (df["lexical_condition"].astype(str) == "natural")
    ]
    if "prompt_variant" in frame.columns:
        frame = frame[frame["prompt_variant"].fillna("canonical") != "alternate"]
    scores = {}
    for model, group in frame.groupby("model"):
        scored = group[group["status"].isin(["CORRECT", "INCORRECT"])]
        if scored.empty:
            continue
        scores[str(model)] = float((scored["status"] == "CORRECT").mean())
    return scores


def _get_field(value: Any, field: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(field, default)
    return getattr(value, field, default)