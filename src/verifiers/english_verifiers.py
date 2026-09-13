# src/verifiers/english_verifiers.py
from typing import Dict, Any, Tuple
from src.verifiers.common import extract_final_choice


def verify_english_agreement_attraction(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    expected = gold_structure["correct_choice"].lower()
    selected = extract_final_choice(model_output, valid_choices=("a", "b"))
    if selected == expected:
        return True, "PASS", {"matched_choice": expected}
    return False, "FAIL_CASE_SELECTION_ERROR", {"selected": selected, "expected": expected, "raw_output": model_output}


def _valid_choices(gold_structure: Dict[str, Any]) -> Tuple[str, ...]:
    n = int(gold_structure.get("n_options") or 3)
    return tuple("abc"[:n])


def _verify_choice(
    model_output: str,
    gold_structure: Dict[str, Any],
    *,
    error_code: str,
    selected_key: str,
    expected_key: str,
) -> Tuple[bool, str, Dict[str, Any]]:
    expected = str(gold_structure["correct_choice"]).lower()
    selected = extract_final_choice(model_output, valid_choices=_valid_choices(gold_structure))
    if selected == expected:
        return True, "PASS", {selected_key: expected}
    return False, error_code, {
        selected_key: selected,
        expected_key: expected,
        "raw_output": model_output,
    }


def verify_english_npi_licensing(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    return _verify_choice(
        model_output,
        gold_structure,
        error_code="FAIL_NPI_LICENSING_ERROR",
        selected_key="selected",
        expected_key="expected",
    )


def verify_english_scalar_implicature(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    return _verify_choice(
        model_output,
        gold_structure,
        error_code="FAIL_SCALAR_IMPLICATURE_ERROR",
        selected_key="selected",
        expected_key="expected",
    )


def verify_english_quantifier_scope(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    return _verify_choice(
        model_output,
        gold_structure,
        error_code="FAIL_QUANTIFIER_SCOPE_ERROR",
        selected_key="selected_scope_choice",
        expected_key="expected_scope_choice",
    )


def verify_english_negation_scope(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies EN Tier 2 (Negation Scope) via forced-choice truth-conditional matching.
    """
    expected_choice = gold_structure["correct_choice"].lower()
    selected_choice = extract_final_choice(model_output)

    if selected_choice == expected_choice:
        return True, "PASS", {"matched_scope_choice": expected_choice}
    else:
        return False, "FAIL_NEGATION_SCOPE_ERROR", {
            "selected_choice": selected_choice,
            "expected_scope_choice": expected_choice,
            "scope_subtree": gold_structure.get("scope_subtree"),
        }
