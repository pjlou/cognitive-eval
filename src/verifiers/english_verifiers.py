# src/verifiers/english_verifiers.py
import spacy
from typing import Dict, Any, Tuple
from src.verifiers.common import extract_final_choice

# Load transformer pipeline for deterministic parse quality
nlp_en = spacy.load("en_core_web_trf")

def verify_english_agreement_attraction(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies EN Tier 1 (Agreement Attraction) using the gold verb target when
    template-based sentence reconstruction is unavailable. Supports both legacy
    template payloads and newer schemas that only carry expected_verb and head metadata.
    """
    expected_verb = str(gold_structure.get("expected_verb", "")).strip().lower()
    gold_head = str(gold_structure.get("syntactic_head", "")).strip().lower()
    attractor = str(gold_structure.get("attractor", "")).strip().lower()
    template = gold_structure.get("template")

    if not expected_verb and isinstance(template, str):
        expected_verb = template.strip().lower()

    if not expected_verb:
        return False, "FAIL_INVALID_GOLD", {
            "reason": "Missing expected_verb and template",
            "raw_gold": gold_structure,
        }

    # Prefer an explicit final-answer marker over the first is/are mentioned
    # anywhere in the output -- a model that reasons out loud before answering
    # (e.g. "the changes are plural, but the list is ready") would otherwise
    # get scored on an incidental token from its own reasoning, not its answer.
    chosen_verb = extract_final_choice(str(model_output or ""), valid_choices=("is", "are"))
    if chosen_verb is None:
        return False, "FAIL_INVALID_OUTPUT", {
            "raw_output": model_output,
            "expected_verb": expected_verb,
            "gold_head": gold_head,
            "attractor_noun": attractor,
        }

    metadata = {
        "chosen_verb": chosen_verb,
        "expected_verb": expected_verb,
        "gold_declared_head": gold_head,
        "attractor_noun": attractor,
    }

    if isinstance(template, str):
        full_sentence = template.format(verb=chosen_verb)
        doc = nlp_en(full_sentence)

        verb_token = next((t for t in doc if t.text.lower() == chosen_verb and t.pos_ in ("AUX", "VERB")), None)
        if verb_token is None:
            return False, "FAIL_PARSE_ERROR", {**metadata, "raw_output": model_output, "reason": "Verb not located in reparsed sentence."}

        subj_token = next((c for c in verb_token.children if c.dep_ == "nsubj"), None)
        if subj_token is None:
            return False, "FAIL_PARSE_ERROR", {**metadata, "raw_output": model_output, "reason": "No nsubj attached to verb."}

        parser_agrees_with_gold_head = (subj_token.text.lower() == gold_head)
        head_number = subj_token.morph.get("Number", None)
        verb_number = verb_token.morph.get("Number", None)
        number_match = bool(head_number) and head_number == verb_number

        metadata.update({
            "parser_identified_head": subj_token.text.lower(),
            "parser_agrees_with_gold_head": parser_agrees_with_gold_head,
            "head_number": head_number,
            "verb_number": verb_number,
        })

        if not parser_agrees_with_gold_head:
            return False, "FLAG_PARSER_DISAGREEMENT", metadata

        if number_match and chosen_verb == expected_verb:
            return True, "PASS", metadata

    if chosen_verb == expected_verb:
        return True, "PASS", metadata

    return False, "FAIL_ATTRACTION_ERROR", {
        **metadata,
        "reason": "Model chose the verb inconsistent with the syntactic head agreement target.",
    }


def verify_english_negation_scope(model_output: str, gold_structure: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies EN Tier 2 (Negation Scope) via forced-choice truth-conditional matching.
    """
    expected_choice = gold_structure["correct_reading"].lower()
    selected_choice = extract_final_choice(model_output)

    if selected_choice == expected_choice:
        return True, "PASS", {"matched_scope_choice": expected_choice}
    else:
        return False, "FAIL_NEGATION_SCOPE_ERROR", {
            "selected_choice": selected_choice,
            "expected_scope_choice": expected_choice,
            "scope_subtree": gold_structure["scope_subtree"]
        }