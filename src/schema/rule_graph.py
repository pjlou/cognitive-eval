# src/schema/rule_graph.py
import networkx as nx
from typing import Dict, Any

def build_v02_rule_graph() -> nx.DiGraph:
    """Builds the grounded rule graph for the 2x2 crossed evaluation suite."""
    G = nx.DiGraph()

    # -------------------------------------------------------------------------
    # FINNISH TIER 1: Object Case Alternation (Kiparsky 1998 Grounded)
    # -------------------------------------------------------------------------
    G.add_node("CAT_FI_POLARITY", type="Category", label="Clause Polarity")
    G.add_node("CAT_FI_ASPECT", type="Category", label="Aspect / Telicity")
    G.add_node("CAT_FI_QUANT", type="Category", label="NP Quantization")
    G.add_node("CAT_FI_CASE", type="Category", label="Grammatical Case Target")

    # Features (Universal Dependencies Vocabulary)
    G.add_node("FEAT_FI_NEG", type="Feature", label="Polarity=Neg")
    G.add_node("FEAT_FI_AFF", type="Feature", label="Polarity=Pos")
    G.add_node("FEAT_FI_ATELIC", type="Feature", label="Aspect=Atelic")
    G.add_node("FEAT_FI_TELIC", type="Feature", label="Aspect=Telic")
    G.add_node("FEAT_FI_QUANTIZED", type="Feature", label="Quant=Bounded")
    G.add_node("FEAT_FI_PARTITIVE", type="Feature", label="Case=Partitive")
    G.add_node("FEAT_FI_ACCUSATIVE", type="Feature", label="Case=Accusative")

    # Kiparsky (1998) Rule Conditions
    G.add_node(
        "RULE_FI_C1_NEGATION",
        type="Rule",
        citation="Kiparsky (1998:271)",
        label="C1: Categorical Negation Rule",
        explanation="Negation categorically selects Partitive object in Finnish, regardless of aspect or quantization."
    )
    G.add_edge("FEAT_FI_NEG", "RULE_FI_C1_NEGATION", relation="TRIGGERS")
    G.add_edge("RULE_FI_C1_NEGATION", "FEAT_FI_PARTITIVE", relation="ENTAILS")

    G.add_node(
        "RULE_FI_C2_ATELIC",
        type="Rule",
        citation="Kiparsky (1998:275)",
        label="C2: Atelic Aspect Rule",
        explanation="Irresultative/ongoing action (Atelic aspect) selects Partitive object case."
    )
    G.add_edge("FEAT_FI_AFF", "RULE_FI_C2_ATELIC", relation="REQUIRES")
    G.add_edge("FEAT_FI_ATELIC", "RULE_FI_C2_ATELIC", relation="TRIGGERS")
    G.add_edge("RULE_FI_C2_ATELIC", "FEAT_FI_PARTITIVE", relation="ENTAILS")

    G.add_node(
        "RULE_FI_C3_TELIC_ACCUSATIVE",
        type="Rule",
        citation="Kiparsky (1998:278)",
        label="C3: Telic Bounded Accusative Rule",
        explanation="Completed action (Telic) with a bounded/quantized object selects Accusative case."
    )
    G.add_edge("FEAT_FI_AFF", "RULE_FI_C3_TELIC_ACCUSATIVE", relation="REQUIRES")
    G.add_edge("FEAT_FI_TELIC", "RULE_FI_C3_TELIC_ACCUSATIVE", relation="REQUIRES")
    G.add_edge("FEAT_FI_QUANTIZED", "RULE_FI_C3_TELIC_ACCUSATIVE", relation="TRIGGERS")
    G.add_edge("RULE_FI_C3_TELIC_ACCUSATIVE", "FEAT_FI_ACCUSATIVE", relation="ENTAILS")

    # -------------------------------------------------------------------------
    # ENGLISH TIER 1: Agreement Attraction (Bock & Miller 1991 Grounded)
    # -------------------------------------------------------------------------
    G.add_node("CAT_EN_NUM", type="Category", label="Grammatical Number")
    G.add_node("FEAT_EN_SG", type="Feature", label="Number=Singular")
    G.add_node("FEAT_EN_PL", type="Feature", label="Number=Plural")

    G.add_node(
        "RULE_EN_AGR_HEAD",
        type="Rule",
        citation="Bock & Miller (1991)",
        label="Head Subject Agreement Rule",
        explanation="Verb agreement must track the number feature of the syntactic head noun (nsubj), ignoring linearly intervening attractor nouns."
    )
    G.add_edge("FEAT_EN_SG", "RULE_EN_AGR_HEAD", relation="TRIGGERS")

    return G

def audit_rule(graph: nx.DiGraph, rule_node_id: str) -> Dict[str, Any]:
    """Provides complete audit trail for why a test item gold label exists."""
    if not graph.has_node(rule_node_id):
        return {"error": f"Rule '{rule_node_id}' not found in rule graph."}
    
    data = graph.nodes[rule_node_id]
    premises = [u for u, v in graph.in_edges(rule_node_id)]
    outcomes = [v for u, v in graph.out_edges(rule_node_id)]
    
    return {
        "rule_id": rule_node_id,
        "label": data.get("label"),
        "citation": data.get("citation"),
        "explanation": data.get("explanation"),
        "triggered_by_features": premises,
        "entails_outcomes": outcomes
    }