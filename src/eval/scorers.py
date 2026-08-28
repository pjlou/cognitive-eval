# src/eval/scorers.py
from inspect_ai.scorer import Scorer, Score, Target, accuracy, stderr, scorer
from inspect_ai.solver import TaskState
from src.verifiers.english_verifiers import verify_english_agreement_attraction, verify_english_negation_scope
from src.verifiers.finnish_verifiers import verify_finnish_object_case, verify_finnish_negation_scope
from src.schema.rule_graph import build_v02_rule_graph, audit_rule

# Initialize static rule graph for metadata enrichment
RULE_GRAPH = build_v02_rule_graph()

@scorer(metrics=[accuracy(), stderr()])
def structural_linguistic_scorer() -> Scorer:
    """
    Inspect Scorer that executes deterministic verifiers based on item metadata.
    Enriches evaluation logs with formal rule graph explanations.
    """
    async def score(state: TaskState, target: Target) -> Score:
        metadata = state.metadata
        model_output = state.output.completion
        
        phenomenon = metadata.get("phenomenon")
        rule_node_id = metadata.get("rule_node_id")
        gold_structure = metadata.get("gold_structure", {})
        
        # Route to deterministic verifier
        if phenomenon == "agreement_attraction":
            passed, error_code, meta = verify_english_agreement_attraction(model_output, gold_structure)
        elif phenomenon == "object_case_alternation":
            passed, error_code, meta = verify_finnish_object_case(model_output, gold_structure)
        elif phenomenon == "negation_scope" and metadata.get("module") == "english":
            passed, error_code, meta = verify_english_negation_scope(model_output, gold_structure)
        elif phenomenon == "negation_scope" and metadata.get("module") == "finnish":
            passed, error_code, meta = verify_finnish_negation_scope(model_output, gold_structure)
        else:
            passed, error_code, meta = False, "FAIL_UNKNOWN_PHENOMENON", {}

        # Fetch rule graph audit trail
        if rule_node_id is None:
            rule_audit = {"label": "N/A", "citation": None, "explanation": None}
        else:
            rule_audit = audit_rule(RULE_GRAPH, rule_node_id)

        return Score(
            value=1.0 if passed else 0.0,
            answer=model_output,
            explanation=f"Verifier Code: {error_code} | Rule: {rule_audit.get('label', 'N/A')}",
            metadata={
                "result": "CORRECT" if passed else "INCORRECT",
                "error_code": error_code,
                "verifier_metadata": meta,
                "rule_citation": rule_audit.get("citation"),
                "rule_explanation": rule_audit.get("explanation")
            }
        )
        
    return score