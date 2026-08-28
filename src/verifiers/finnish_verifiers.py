# src/verifiers/finnish_verifiers.py
from typing import Dict, Any, Tuple
from uralicNLP import uralicApi as uralicNLP

def verify_finnish_object_case(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies FI Tier 1 (Object Case Alternation).
    Extracts morphological features for target noun tokens in the model response
    and verifies whether case matches Partitive or Accusative rules (Kiparsky 1998).
    """
    cleaned_output = model_output.strip().replace(".", "").replace(",", "")
    words = cleaned_output.split()
    target_lemma = gold_structure.get("target_lemma")
    expected_case = gold_structure["expected_case"]  # "Partitive" or "Accusative"
    expected_form = gold_structure.get("expected_form")
    
    extracted_tags = []
    found_correct_case = False
    
    for word in words:
        analyses = uralicNLP.analyze(word, "fin")
        for analysis, cost in analyses:
            tags = analysis.split("+")
            lemma_matches = target_lemma is None or analysis.startswith(f"{target_lemma}+")
            form_matches = expected_form is None or word.lower() == expected_form.lower()
            # Check morphological tags for target case
            if lemma_matches and form_matches and expected_case == "Partitive" and "Par" in tags:
                found_correct_case = True
                extracted_tags.append(analysis)
            elif lemma_matches and form_matches and expected_case == "Accusative" and (
                "Gen" in tags or "Acc" in tags or "Nom" in tags
            ):
                found_correct_case = True
                extracted_tags.append(analysis)
                
    if found_correct_case:
        return True, "PASS", {"expected_case": expected_case, "matched_analyses": extracted_tags}
    else:
        return False, "FAIL_CASE_SELECTION_ERROR", {
            "expected_case": expected_case,
            "condition_violated": gold_structure.get("condition", "UNKNOWN"),
            "raw_output": model_output
        }


def verify_finnish_negation_scope(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies FI Tier 2 (Connegative / Negation Scope).
    Checks reading selection for scope Interaction with quantifiers (kaikki eivät...).
    """
    expected_choice = gold_structure["correct_reading"].lower()
    cleaned = model_output.strip().lower()
    
    if cleaned.startswith(expected_choice) or f"({expected_choice})" in cleaned:
        return True, "PASS", {"matched_scope_choice": expected_choice}
    else:
        return False, "FAIL_FI_NEGATION_SCOPE_ERROR", {
            "expected_choice": expected_choice,
            "raw_output": model_output
        }