# src/verifiers/english_verifiers.py
import spacy
from typing import Dict, Any, Tuple

# Load transformer pipeline for deterministic parse quality
nlp_en = spacy.load("en_core_web_trf")

def verify_english_agreement_attraction(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies EN Tier 1 (Agreement Attraction).
    Extracts the verb from the model's output and verifies if its number matches
    the syntactic head noun rather than an intervening distractor.
    """
    doc = nlp_en(model_output.strip())
    expected_verb = gold_structure["expected_verb"].lower()
    
    # Simple extraction check for single-word or short responses
    extracted_words = [token.text.lower() for token in doc if token.is_alpha]
    
    if expected_verb in extracted_words:
        return True, "PASS", {"extracted_verb": expected_verb, "head_target": gold_structure["syntactic_head"]}
    else:
        # Detect if model fell for the attractor distractor
        distractor_verb = "are" if expected_verb == "is" else "is"
        if distractor_verb in extracted_words:
            return False, "FAIL_ATTRACTION_ERROR", {
                "extracted_verb": distractor_verb,
                "attractor_noun": gold_structure["attractor"],
                "reason": "Model agreed with distractor noun instead of head subject."
            }
        return False, "FAIL_INVALID_OUTPUT", {"raw_output": model_output}


def verify_english_negation_scope(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies EN Tier 2 (Negation Scope).
    Checks if the model selected the correct structural scope reading (e.g., 'a', 'b', or 'c').
    """
    doc = nlp_en(model_output.strip().lower())
    expected_choice = gold_structure["correct_reading"].lower()
    
    # Extract letter choices or explicit scope statements
    first_char = model_output.strip().lower()[0] if model_output.strip() else ""
    
    if first_char == expected_choice or f"({expected_choice})" in model_output.lower():
        return True, "PASS", {"matched_scope_choice": expected_choice}
    else:
        return False, "FAIL_NEGATION_SCOPE_ERROR", {
            "selected_choice": first_char,
            "expected_scope_choice": expected_choice,
            "scope_subtree": gold_structure["scope_subtree"]
        }