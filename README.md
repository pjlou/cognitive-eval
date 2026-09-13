# Cognitive-Eval: Diagnostic LLM Linguistic Evaluation Framework (v0.2)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Inspect AI Framework](https://img.shields.io/badge/Inspect_AI-UK_AISI-purple.svg)](https://github.com/UKGovernmentBEIS/inspect_ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Cognitive-Eval** is an open-source diagnostic evaluation framework designed to identify structural semantic and morphosyntactic failure modes in Large Language Models (LLMs).  Its primary purpose is to examine whether a model's linguistic competence is genuinely structural or a surface artifact of memorized vocabulary, using models small enough to run on consumer-grade devices.  Models in the included evaluation logs cover different sizes within the qwen2.5 family (1.5b, 3b, and 7b parameters) as well as ministral-3:8b and llama3.1:8b

---

## Architecture Overview

Cognitive-Eval employs a **2 (Tier) × 2 (Lexical condition) crossed experimental design** to test whether a model's linguistic competence is genuinely structural or merely a surface artifact of memorized vocabulary. Every phenomenon, in both tiers and both conditions, is verified via **forced-choice truth-conditional matching** against a grounded rule graph (`NetworkX`) — this was a deliberate change from an earlier version, in which Tier 1 (morphological) items required the model to freely generate an inflected word form. That format difference turned out to be a confound: it made Tier 1 and Tier 2 accuracy numbers incomparable, since one measured production ability and the other measured selection/reasoning ability. Forced-choice for everything removes that confound. The second axis is a wug-test contrast (Berko 1958): **natural** items use existing English vocabulary, and **novel** items keep closed-class words real while swapping open-class content words for invented ones with regular morphology. The same English verifier and rule node score both conditions, so a natural-versus-novel accuracy gap is lexical familiarity, not a change in the rule being tested. `spaCy` is used to inspect English structure, not to score free-form output at run time.

Free-form generation hasn't disappeared from the project — it's been moved to where it belongs methodologically. See **"Verification Cascade"** below.

                     ┌───────────────────────────────────────────────────────────┐
                     │          Crossed Tier x Lexical Evaluation Grid           │
                     ├─────────────────────────────┬─────────────────────────────┤
                     │     Natural vocabulary      │     Novel vocabulary        │
    ┌────────────────┼─────────────────────────────┼─────────────────────────────┤
    │ Tier 1: Local  │ Subject–Verb Agreement      │ Same rule, novel nouns      │
    │ Morphosyntax   │ (Attraction Paradigms)      │ with regular inflection     │
    ├────────────────┼─────────────────────────────┼─────────────────────────────┤
    │ Tier 2: Clausal│ Negation scope, NPI         │ Same rules, novel content   │
    │ Semantics      │ licensing, scalar           │ words, real function words  │
    │                │ implicature, quantifier     │                             │
    │                │ scope (disambiguated)       │                             │
    ├────────────────┼─────────────────────────────┼─────────────────────────────┤
    │ Stage 3        │ Quantifier-scope            │ Same continuation, novel    │
    │                │ justification (judge rubric)│ open-class words            │
    └────────────────┴─────────────────────────────┴─────────────────────────────┘


Every test result is linked directly to a formal rule node in a NetworkX graph grounded in computational linguistics literature (**Bock & Miller 1991** for agreement attraction; **ScoNe 2023** for negation scope; **Ladusaw 1979** for NPI licensing; **Grice 1975 / Levinson 2000** for scalar implicature; **Ioup 1975 / Anderson 2004** for quantifier scope). Novel items reuse those same rule nodes. Item-construction rules, including the novel-word generator and the contamination argument for the novel-lexical control, are in `docs/item-construction.md`. Cross-linguistic comparison remains a deferred stretch goal, not a current axis.

---

## Verification Cascade

This project does not treat "verify against a rule" and "ask an LLM to judge" as
a binary choice. It uses a **cascade**: the cheapest method that can actually
resolve a question runs first, and more expensive methods are used only where
a cheaper one genuinely can't apply.

```
Stage 1 (implemented)   Rule-based / deterministic verification
                          — src/verifiers, forced-choice against the rule graph
                          — cheapest, fastest, fully auditable
                          — requires a phenomenon to already have a known rule

Stage 2 (implemented)   Statistical / embedding-based failure discovery
                          — src/discovery — unsupervised, no gold label needed
                          — finds candidate failure PATTERNS in free-form
                            generation, for a human to inspect
                          — a cluster judged genuine and coherent gets promoted
                            into a new Stage 1 rule graph node -- discovery
                            happens once, at Stage 2 cost; detection is cheap
                            (Stage 1) from then on

Stage 3 (scoped)        Model-based judgment against a disclosed rubric
                          — quantifier-scope justification items only
                          — not a general-purpose "ask an LLM if this is right"

Stage 4 (documented)    Human review — the fallback when Stage 3 disagrees
                          with itself across runs or confidence is low
```

### Stage 2: Statistical Failure Discovery

`src/discovery` collects free-form (non-graded, non-multiple-choice) generations
from local models on prompts covering the same phenomena as the graded suite,
but with different lexical items and quantifiers than appear anywhere in the
scored dataset — so a discovered cluster is a genuinely new observation, not a
rediscovery of a graded example. Responses are embedded and clustered (KMeans
and DBSCAN, compared against each other since DBSCAN can isolate a rare,
interesting outlier that KMeans would force into a nearby cluster), and the
clustering/summarization logic is unit-tested against synthetic embeddings in
`tests/test_discovery.py` so it doesn't depend on the embedding model being
downloaded to verify correctness.

To run it:
```bash
python -m src.discovery.generate_free_responses
python -m src.discovery.cluster_failures
streamlit run dashboard/app.py   # see the new "Cascade Stage 2" panel
```

This produces `discovery_logs/cluster_summary.json` (per-cluster size, model
distribution, and nearest-to-centroid example texts for review) and
`discovery_logs/cluster_points.json` (a 2D PCA projection for the dashboard
scatter plot). Nothing here is scored — the output is a set of clusters for a
human to read, not a benchmark result.

---

## Quick Start Guide

### 1. Installation & Environment Setup
```bash
git clone https://github.com/pjlou/Cognitive-Eval.git
cd Cognitive-Eval

python3.11 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_trf
```

### 2. Run Evaluations via Inspect AI
Execute the benchmark across local (Ollama) targets:

```bash
python run_evals.py
```

### 3. Launch Dashboard
Visualize evaluation logs, error taxonomies, and dependency parse trees:

```bash
streamlit run dashboard/app.py
```

### 4. (Optional) Run Statistical Failure Discovery
See "Verification Cascade" below for what this does and why it's separate
from the graded suite above.

```bash
python -m src.discovery.generate_free_responses
python -m src.discovery.cluster_failures
```

## Citation & Grounding
Berko, J. (1958). The child's learning of English morphology. Word.

Bock, K., & Miller, C. A. (1991). Broken agreement. Cognitive Psychology.

Warstadt et al. (2020). BLiMP: Benchmark of Linguistic Minimal Pairs. TACL.