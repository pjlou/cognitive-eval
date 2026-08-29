# Cognitive-Eval: Diagnostic LLM Linguistic Evaluation Framework (v0.2)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Inspect AI Framework](https://img.shields.io/badge/Inspect_AI-UK_AISI-purple.svg)](https://github.com/UKGovernmentBEIS/inspect_ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Cognitive-Eval** is an open-source diagnostic evaluation framework designed to identify structural semantic and morphosyntactic failure modes in Large Language Models (LLMs). 

Unlike subjective "LLM-as-a-judge" evaluation pipelines, every test in this suite is verified **deterministically** against dependency parse trees (`spaCy`), morphological feature sets (`UralicNLP`), and a grounded rule graph (`NetworkX`).

---

## Architecture Overview

Cognitive-Eval employs a **2 (Tier) × 2 (Language) crossed experimental design** to test whether a model's linguistic competence is genuinely structural or merely a surface artifact of English-dominant training data.

                     ┌───────────────────────────────────────────────────────────┐
                     │                Crossed 2x2 Evaluation Grid                │
                     ├─────────────────────────────┬─────────────────────────────┤
                     │           English           │           Finnish           │
    ┌────────────────┼─────────────────────────────┼─────────────────────────────┤
    │ Tier 1: Local  │ Subject–Verb Agreement      │ Object Case Alternation     │
    │ Morphosyntax   │ (Attraction Paradigms)      │ (Partitive vs. Accusative)  │
    ├────────────────┼─────────────────────────────┼─────────────────────────────┤
    │ Tier 2: Clausal│ Negation Scope              │ Connegative Construction &  │
    │ Semantics      │ (Subtree Scope Attachment)  │ Focus Clitic Scope          │
    └────────────────┴─────────────────────────────┴─────────────────────────────┘


Every test result is linked directly to a formal rule node in a NetworkX graph grounded in computational linguistics literature (e.g., **Kiparsky 1998** for Finnish aspect/case; **Bock & Miller 1991** for agreement attraction).

---

## Quick Start Guide

### 1. Installation & Environment Setup
```bash
git clone [https://github.com/pjlou/Cognitive-Eval.git](https://github.com/pjlou/Cognitive-Eval.git)
cd Cognitive-Eval

python3.11 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_trf
python -c "import uralicNLP"
```

### 2. Run Evaluations via Inspect AI
Execute the benchmark across local (Ollama) and API-based model targets:

```bash
python run_evals.py
```

### 3. Launch Dashboard
Visualize evaluation logs, error taxonomies, and dependency parse trees:

```bash
streamlit run dashboard/app.py
```

## Citation & Grounding
Kiparsky, P. (1998). Partitive case and aspect. CSLI Publications.

Bock, K., & Miller, C. A. (1991). Broken agreement. Cognitive Psychology.

Warstadt et al. (2020). BLiMP: Benchmark of Linguistic Minimal Pairs. TACL.