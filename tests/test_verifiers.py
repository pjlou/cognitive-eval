# tests/test_verifiers.py
from src.verifiers.english_verifiers import (
    verify_english_agreement_attraction,
    verify_english_negation_scope,
    verify_english_npi_licensing,
    verify_english_quantifier_scope,
    verify_english_scalar_implicature,
)


def test_en_agreement_attraction_pass():
    gold = {"syntactic_head": "list", "attractor": "changes", "correct_choice": "a"}
    passed, error_code, meta = verify_english_agreement_attraction("a", gold)
    assert passed is True
    assert error_code == "PASS"
    assert meta["matched_choice"] == "a"


def test_en_agreement_attraction_attractor_fail():
    gold = {"syntactic_head": "list", "attractor": "changes", "correct_choice": "a"}
    passed, error_code, meta = verify_english_agreement_attraction("b", gold)
    assert passed is False
    assert error_code == "FAIL_CASE_SELECTION_ERROR"
    assert meta["selected"] == "b"
    assert meta["expected"] == "a"


def test_en_agreement_attraction_ignores_distractor_in_reasoning_trace():
    gold = {"syntactic_head": "list", "attractor": "changes", "correct_choice": "a"}
    reasoning_output = (
        "Option b is tempting because 'changes' is plural, "
        "but the syntactic head 'list' is singular, so the correct answer is a."
    )
    passed, error_code, meta = verify_english_agreement_attraction(reasoning_output, gold)
    assert passed is True
    assert error_code == "PASS"
    assert meta["matched_choice"] == "a"


def test_en_agreement_attraction_honors_explicit_final_answer_marker():
    gold = {"syntactic_head": "lists", "attractor": "report", "correct_choice": "b"}
    reasoning_output = "The report is singular, but the head is plural. Final answer: b"
    passed, error_code, meta = verify_english_agreement_attraction(reasoning_output, gold)
    assert passed is True
    assert error_code == "PASS"
    assert meta["matched_choice"] == "b"


def test_en_agreement_attraction_no_valid_choice_found():
    gold = {"syntactic_head": "list", "attractor": "changes", "correct_choice": "a"}
    passed, error_code, meta = verify_english_agreement_attraction("I'm not sure.", gold)
    assert passed is False
    assert error_code == "FAIL_CASE_SELECTION_ERROR"
    assert meta["selected"] is None


def test_en_negation_scope_pass():
    gold = {"correct_choice": "b", "scope_subtree": "all students ... failed"}
    passed, error_code, meta = verify_english_negation_scope("b", gold)
    assert passed is True
    assert error_code == "PASS"


def test_novel_agreement_uses_the_same_verifier():
    """Novel-word gold does not require a new verifier; only correct_choice is scored."""
    gold = {
        "syntactic_head": "wug",
        "head_number": "singular",
        "attractor": "blorptors",
        "attractor_number": "plural",
        "correct_choice": "a",
    }
    passed, error_code, meta = verify_english_agreement_attraction("a", gold)
    assert passed is True
    assert error_code == "PASS"
    assert meta["matched_choice"] == "a"

    failed, fail_code, fail_meta = verify_english_agreement_attraction("b", gold)
    assert failed is False
    assert fail_code == "FAIL_CASE_SELECTION_ERROR"
    assert fail_meta["expected"] == "a"


def test_novel_negation_uses_the_same_verifier():
    """Novel-word gold does not require a new verifier; not-all still expects choice b."""
    gold = {
        "negation_governor": "vorped",
        "scope_subtree": "all the glorbs ... vorped",
        "correct_choice": "b",
    }
    passed, error_code, meta = verify_english_negation_scope("b", gold)
    assert passed is True
    assert error_code == "PASS"
    assert meta["matched_scope_choice"] == "b"

    failed, fail_code, fail_meta = verify_english_negation_scope("a", gold)
    assert failed is False
    assert fail_code == "FAIL_NEGATION_SCOPE_ERROR"
    assert fail_meta["expected_scope_choice"] == "b"
    assert fail_meta["scope_subtree"] == "all the glorbs ... vorped"


def test_npi_scalar_and_scope_verifiers_score_the_letter_only():
    npi = {"correct_choice": "a", "n_options": 2}
    passed, code, _meta = verify_english_npi_licensing("The answer is a.", npi)
    assert passed and code == "PASS"
    failed, fail_code, _meta = verify_english_npi_licensing("b", npi)
    assert not failed and fail_code == "FAIL_NPI_LICENSING_ERROR"

    scalar = {"correct_choice": "b", "n_options": 3}
    passed, code, _meta = verify_english_scalar_implicature("final answer: b", scalar)
    assert passed and code == "PASS"

    scope = {"correct_choice": "c", "n_options": 3}
    passed, code, _meta = verify_english_quantifier_scope("c", scope)
    assert passed and code == "PASS"
    failed, fail_code, _meta = verify_english_quantifier_scope("a", scope)
    assert not failed and fail_code == "FAIL_QUANTIFIER_SCOPE_ERROR"
