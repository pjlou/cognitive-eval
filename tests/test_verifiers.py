# tests/test_verifiers.py
import pytest
from src.verifiers.english_verifiers import verify_english_agreement_attraction, verify_english_negation_scope
from src.verifiers.finnish_verifiers import verify_finnish_object_case

def test_en_agreement_attraction_pass():
    gold = {"syntactic_head": "list", "attractor": "changes", "expected_verb": "is"}
    passed, error_code, meta = verify_english_agreement_attraction("is", gold)
    assert passed is True
    assert error_code == "PASS"

def test_en_agreement_attraction_attractor_fail():
    gold = {"syntactic_head": "list", "attractor": "changes", "expected_verb": "is"}
    passed, error_code, meta = verify_english_agreement_attraction("are", gold)
    assert passed is False
    assert error_code == "FAIL_ATTRACTION_ERROR"
    assert meta["attractor_noun"] == "changes"

def test_en_agreement_attraction_ignores_distractor_in_reasoning_trace():
    # A model that reasons out loud before answering will often mention the
    # WRONG verb form first (describing the attractor noun) before settling
    # on its real answer. Prior to the extraction fix, this was scored on
    # the first is/are token and would have failed incorrectly.
    gold = {"syntactic_head": "list", "attractor": "changes", "expected_verb": "is"}
    reasoning_output = (
        "The changes are numerous, but the syntactic head 'list' is singular, "
        "so the correct answer is 'is'."
    )
    passed, error_code, meta = verify_english_agreement_attraction(reasoning_output, gold)
    assert passed is True
    assert error_code == "PASS"
    assert meta["chosen_verb"] == "is"

def test_en_agreement_attraction_honors_explicit_final_answer_marker():
    gold = {"syntactic_head": "lists", "attractor": "report", "expected_verb": "are"}
    reasoning_output = "The report is singular, but the head is plural. Final answer: are"
    passed, error_code, meta = verify_english_agreement_attraction(reasoning_output, gold)
    assert passed is True
    assert error_code == "PASS"
    assert meta["chosen_verb"] == "are"

def test_en_agreement_attraction_no_valid_verb_found():
    gold = {"syntactic_head": "list", "attractor": "changes", "expected_verb": "is"}
    passed, error_code, meta = verify_english_agreement_attraction("I'm not sure.", gold)
    assert passed is False
    assert error_code == "FAIL_INVALID_OUTPUT"

def test_fi_object_case_partitive_pass():
    gold = {"target_lemma": "omena", "expected_case": "Partitive", "condition": "C2"}
    passed, error_code, meta = verify_finnish_object_case("Söin omenaa", gold)
    assert passed is True
    assert error_code == "PASS"

def test_fi_object_case_accusative_fail():
    gold = {"target_lemma": "omena", "expected_case": "Partitive", "condition": "C1"}
    # Passing accusative 'omenan' when Partitive is expected
    passed, error_code, meta = verify_finnish_object_case("Söin omenan", gold)
    assert passed is False
    assert error_code == "FAIL_CASE_SELECTION_ERROR"