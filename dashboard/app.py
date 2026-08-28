# dashboard/app.py
import streamlit as st
import pandas as pd
import spacy
from spacy import displacy
from utils import load_eval_logs
from src.schema.rule_graph import build_v02_rule_graph, audit_rule

# Page Configuration
st.set_page_config(
    page_title="Cognitive-Eval Dashboard",
    page_icon="🧠",
    layout="wide"
)

# Load spaCy model for live visualization
@st.cache_resource
def load_spacy_model():
    return spacy.load("en_core_web_trf")

nlp_en = load_spacy_model()
rule_graph = build_v02_rule_graph()

# Header & Overview
st.title("🧠 Cognitive-Eval: Structural LLM Diagnostic Benchmark")
st.markdown("""
**Version 0.2** | Deterministic evaluation of structural semantics and morphosyntax across English and Finnish minimal pairs.
""")

# Load Data
df = load_eval_logs()

if df.empty:
    st.warning("No evaluation logs found in `./eval_logs`. Run Phase 5 (`run_evals.py`) to populate the dashboard.")
    st.stop()

# Top-level Metric Cards
st.subheader("Global Benchmark Metrics")
col1, col2, col3, col4 = st.columns(4)

total_tests = len(df)
accuracy = (df["status"] == "CORRECT").mean() * 100
models_tested = df["model"].nunique()
phenomena_count = df["phenomenon"].nunique()

col1.metric("Total Tests Evaluated", total_tests)
col2.metric("Overall Pass Rate", f"{accuracy:.1f}%")
col3.metric("Model Families Tested", models_tested)
col4.metric("Active Phenomena", phenomena_count)

st.divider()

# Sidebar Filters
st.sidebar.header("Filter Results")
selected_model = st.sidebar.multiselect("Select Model(s)", options=df["model"].unique(), default=df["model"].unique())
selected_module = st.sidebar.multiselect("Select Module", options=df["module"].unique(), default=df["module"].unique())
selected_tier = st.sidebar.multiselect("Select Tier", options=df["tier"].unique(), default=df["tier"].unique())

filtered_df = df[
    (df["model"].isin(selected_model)) &
    (df["module"].isin(selected_module)) &
    (df["tier"].isin(selected_tier))
]

# Section 1: Accuracy Matrix by Phenomenon & Model
st.subheader("Accuracy Breakdown by Phenomenon & Model Family")

pivot_df = filtered_df.groupby(["phenomenon", "model"])["status"].apply(lambda x: (x == "CORRECT").mean() * 100).unstack()
st.dataframe(pivot_df.style.highlight_max(axis=1, color="lightgreen").format("{:.1f}%"), use_container_width=True)

# Section 2: Error Taxonomy Analysis
st.subheader("Structured Error Taxonomy")
error_df = filtered_df[filtered_df["status"] == "INCORRECT"]["error_code"].value_counts().reset_index()
error_df.columns = ["Error Code / Failure Mode", "Occurrences"]
st.bar_chart(error_df.set_index("Error Code / Failure Mode"))

st.divider()

# Section 3: Interactive Inspector & Dependency Parser Visualizer
st.subheader("Interactive Inspector & Dependency Parse Audit Trail")

selected_sample_id = st.selectbox("Select Sample ID to Inspect", options=filtered_df["sample_id"].unique())
sample_data = filtered_df[filtered_df["sample_id"] == selected_sample_id].iloc[0]

inspect_col1, inspect_col2 = st.columns(2)

with inspect_col1:
    st.markdown(f"**Sample ID:** `{sample_data['sample_id']}`")
    st.markdown(f"**Target Model:** `{sample_data['model']}`")
    st.markdown(f"**Prompt Sent to LLM:**")
    st.info(sample_data["prompt"])
    st.markdown(f"**Raw Model Response:**")
    st.code(sample_data["raw_output"])

with inspect_col2:
    st.markdown("**Rule Graph Audit Trail (Grounded Explanation):**")
    st.json({
        "rule_id": sample_data["rule_node_id"],
        "citation": sample_data["rule_citation"],
        "explanation": sample_data["rule_explanation"],
        "verifier_metadata": sample_data["verifier_metadata"]
    })

# Render spaCy Dependency Parse Tree for English Samples
if sample_data["language"] == "en":
    st.subheader("Live Dependency Parse Tree (spaCy `en_core_web_trf`)")
    doc = nlp_en(sample_data["raw_output"])
    html_dep = displacy.render(doc, style="dep", page=False)
    st.components.v1.html(html_dep, height=350, scrolling=True)