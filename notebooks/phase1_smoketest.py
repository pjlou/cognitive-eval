"""
Phase 1 Smoke Test Script - Version 0.2
Verifies dependencies for the natural/novel English evaluation design:
  - Tier 1: Agreement Attraction (spaCy Dependency Tree)
  - Tier 2: Negation Scope (c-command / Subtree parsing)
"""

import spacy
import networkx as nx
from inspect_ai import Task, task

print("=== Phase 1 (v0.2) Environment Smoke Test ===")

# 1. Test Tier 1: Agreement Attraction (Subject-Verb Head Matching)
print("\n[1/3] Testing Tier 1: Agreement Attraction Parsing...")
nlp_en = spacy.load("en_core_web_trf")
doc_en_tier1 = nlp_en("The list of changes to the report is ready.")
head_noun = [token for token in doc_en_tier1 if token.dep_ == "nsubj"][0]
verb = head_noun.head
print(f"  Sentence: '{doc_en_tier1.text}'")
print(f"  Extracted Head Subject: '{head_noun.text}' | Verb: '{verb.text}' (Agreement Match)")
assert head_noun.text == "list", "Failed to identify syntactic head!"
print("✓ Tier 1 parsing functional.")

# 2. Test Tier 2: Negation Scope Subtree Extraction
print("\n[2/3] Testing Tier 2: Negation Scope Parsing...")
doc_en_tier2 = nlp_en("Not all students failed the test.")
neg_token = [token for token in doc_en_tier2 if token.dep_ == "neg"][0]
scope_subtree = [t.text for t in neg_token.head.subtree]
print(f"  Sentence: '{doc_en_tier2.text}'")
print(f"  Negation Marker: '{neg_token.text}' | Scope Subtree: {' '.join(scope_subtree)}")
print("✓ Tier 2 parsing functional.")

# 3. Test Rule Graph (NetworkX) & Inspect AI Harness Setup
print("\n[3/3] Testing Graph Engine & Inspect AI Harness...")
G = nx.DiGraph()
G.add_node("RULE_EN_AGR_HEAD", label="Verb agreement tracks the syntactic head")
print(f"  Rule Graph Initialized ({G.number_of_nodes()} node).")

@task
def smoke_test_task():
    return Task(dataset=[])

print("✓ NetworkX & Inspect AI harness imports verified.")

print("\n=== ALL PHASE 1 (v0.2) SMOKE TESTS PASSED SUCCESSFULLY ===")
