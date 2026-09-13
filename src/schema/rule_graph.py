# src/schema/rule_graph.py
import networkx as nx
from typing import Dict, Any

def build_v02_rule_graph() -> nx.DiGraph:
    """Builds the grounded rule graph for the natural/novel English suite."""
    G = nx.DiGraph()

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

    
    # -------------------------------------------------------------------------
    # ENGLISH TIER 2: Negation Scope
    # -------------------------------------------------------------------------
    G.add_node("CAT_EN_NEG_SCOPE", type="Category", label="Negation Scope Domain")
    G.add_node("FEAT_EN_EXTERNAL_NEG", type="Feature", label="Negation=External(¬∀)")
    G.add_node(
        "RULE_EN_NEG_SCOPE",
        type="Rule",
        citation="Structural def. per UD c-command (Section 6); items cross-checked against ScoNe (2023)",
        label="External Negation over Universal Quantifier",
        explanation="'Not all X verb' negates the universal claim externally (¬∀x.Vx), which is logically equivalent to 'some X don't verb' (∃x.¬Vx) — i.e. at least one member is exempt, not that none satisfy V."
    )
    G.add_edge("FEAT_EN_EXTERNAL_NEG", "RULE_EN_NEG_SCOPE", relation="TRIGGERS")

    G.add_node("FEAT_EN_NEG_EXISTENTIAL", type="Feature", label="Negation=OfExistential(\u00ac\u2203\u2192\u2200\u00ac)")
    G.add_node(
        "RULE_EN_NEG_UNIVERSAL_QUANT",
        type="Rule",
        citation="Barwise & Cooper (1981) generalized quantifiers; contrastive design per ScoNe (2023)",
        label="Negation of Existential Quantifier ('none of the X')",
        explanation=(
            "'None of the X V' negates an existential claim (\u00ac\u2203x.Vx), which by quantifier "
            "duality is equivalent to a universal negative (\u2200x.\u00acVx) -- every member fails to "
            "satisfy V. This is the minimal contrast to RULE_EN_NEG_SCOPE: 'not all X V' negates "
            "a universal (\u00ac\u2200x.Vx, some don't), while 'none of the X V' negates an existential "
            "(\u00ac\u2203x.Vx, none do) -- a distinction LLMs are known to conflate."
        )
    )
    G.add_edge("FEAT_EN_NEG_EXISTENTIAL", "RULE_EN_NEG_UNIVERSAL_QUANT", relation="TRIGGERS")

    # -------------------------------------------------------------------------
    # ENGLISH: NPI licensing (Ladusaw 1979)
    # -------------------------------------------------------------------------
    G.add_node("CAT_EN_NPI", type="Category", label="Negative Polarity Item Licensing")
    G.add_node("FEAT_EN_DOWNWARD", type="Feature", label="Licensor=DownwardEntailing")
    G.add_node(
        "RULE_EN_NPI_LICENSE",
        type="Rule",
        citation="Ladusaw (1979)",
        label="Any licensed only in a downward-entailing context",
        explanation=(
            "The polarity item 'any' is licensed under negation and other downward-entailing "
            "operators, and is illicit in a plain affirmative clause. Closed-class 'any' and "
            "negation stay real in the novel-lexical condition."
        ),
    )
    G.add_edge("FEAT_EN_DOWNWARD", "RULE_EN_NPI_LICENSE", relation="TRIGGERS")

    # -------------------------------------------------------------------------
    # ENGLISH: Scalar implicature (Grice 1975; Levinson 2000)
    # -------------------------------------------------------------------------
    G.add_node("CAT_EN_SCALAR", type="Category", label="Scalar Implicature")
    G.add_node("FEAT_EN_SOME", type="Feature", label="Quantifier=Some")
    G.add_node(
        "RULE_EN_SCALAR_SOME",
        type="Rule",
        citation="Grice (1975); Levinson (2000)",
        label="Some pragmatically implicates not-all",
        explanation=(
            "On its pragmatic reading, 'some' communicates 'not all' by the quantity maxim: "
            "a cooperative speaker who knew that all was true would have said 'all'. The "
            "logical reading (at least one, possibly all) is a distractor, not the communicated meaning."
        ),
    )
    G.add_edge("FEAT_EN_SOME", "RULE_EN_SCALAR_SOME", relation="TRIGGERS")
    G.add_node(
        "RULE_EN_SCALAR_UNIVERSAL",
        type="Rule",
        citation="Grice (1975); Levinson (2000)",
        label="All does not implicate not-all",
        explanation=(
            "A speaker who says 'all' is asserting the stronger scale-mate. The pragmatic "
            "not-all implicature attaches to 'some', not to 'all'."
        ),
    )
    G.add_edge("FEAT_EN_SOME", "RULE_EN_SCALAR_UNIVERSAL", relation="CONTRASTS")

    # -------------------------------------------------------------------------
    # ENGLISH: Quantifier-quantifier scope (Ioup 1975; Anderson 2004)
    # -------------------------------------------------------------------------
    G.add_node("CAT_EN_QSCOPE", type="Category", label="Quantifier Scope")
    G.add_node("FEAT_EN_SURFACE", type="Feature", label="Scope=Surface(forall>exists)")
    G.add_node("FEAT_EN_INVERSE", type="Feature", label="Scope=Inverse(exists>forall)")
    G.add_node(
        "RULE_EN_QSCOPE_SURFACE",
        type="Rule",
        citation="Ioup (1975); Anderson (2004)",
        label="Surface scope of every over some",
        explanation=(
            "With a continuation that assigns a different witness to each restricter entity "
            "('a different book for each student'), the only consistent reading is surface "
            "scope: every student read a possibly different book."
        ),
    )
    G.add_node(
        "RULE_EN_QSCOPE_INVERSE",
        type="Rule",
        citation="Ioup (1975); Anderson (2004)",
        label="Inverse scope of some over every",
        explanation=(
            "With a continuation that identifies a single shared witness ('the same book for "
            "everyone'), the only consistent reading is inverse scope: there is a book that "
            "every student read. Scope items are not scored without that disambiguating continuation."
        ),
    )
    G.add_edge("FEAT_EN_SURFACE", "RULE_EN_QSCOPE_SURFACE", relation="TRIGGERS")
    G.add_edge("FEAT_EN_INVERSE", "RULE_EN_QSCOPE_INVERSE", relation="TRIGGERS")

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
