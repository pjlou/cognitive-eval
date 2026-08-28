# test_phase2.py
from src.schema.test_item import TestItem
from src.schema.rule_graph import build_v02_rule_graph, audit_rule

# Initialize Rule Graph
graph = build_v02_rule_graph()
print(f"✓ Rule Graph v0.2 loaded ({graph.number_of_nodes()} nodes).")

# Validate Sample Item against Pydantic
sample_item_json = {
    "id": "fi-case-001a",
    "module": "finnish",
    "tier": "tier_1_morphological",
    "phenomenon": "object_case_alternation",
    "language": "fi",
    "prompt": "Complete with correct object: 'Söin __ (omena, partial reading).'",
    "gold_structure": {
        "condition": "C2",
        "expected_case": "Partitive",
        "expected_form": "omenaa"
    },
    "rule_node_id": "RULE_FI_C2_ATELIC",
    "verification_method": "morphological_feature",
    "difficulty": "easy",
    "source": "Kiparsky 1998"
}

item = TestItem(**sample_item_json)
print(f"✓ TestItem Pydantic schema validation passed for ID: {item.id}")

# Perform Audit Trail Lookup
audit = audit_rule(graph, item.rule_node_id)
print("\n--- Rule Graph Audit Trail (Grounded in Literature) ---")
print(f"Rule ID:     {audit['rule_id']}")
print(f"Citation:    {audit['citation']}")
print(f"Label:       {audit['label']}")
print(f"Explanation: {audit['explanation']}")
print(f"Premises:    {audit['triggered_by_features']}")
print(f"Outcomes:    {audit['entails_outcomes']}")
print("---------------------------------------------------------")