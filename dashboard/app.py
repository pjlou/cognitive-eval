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

# Section 1: Accuracy Matrix by Language, Phenomenon & Model
st.subheader("Accuracy Breakdown by Language, Phenomenon & Model Family")

pivot_df = (
    filtered_df.groupby(["language", "phenomenon", "model"])["status"]
    .apply(lambda x: (x == "CORRECT").mean() * 100)
    .unstack("model")
    .reset_index()
)
pivot_df["phenomenon"] = pivot_df["language"].str.upper() + " - " + pivot_df["phenomenon"]
pivot_df = pivot_df.drop(columns="language").set_index("phenomenon")
st.dataframe(pivot_df.style.highlight_max(axis=1, color="lightgreen").format("{:.1f}%"), use_container_width=True)

# Section 2: Error Taxonomy Analysis
st.subheader("Structured Error Taxonomy")
error_df = filtered_df[filtered_df["status"] == "INCORRECT"]["error_code"].value_counts().reset_index()
error_df.columns = ["Error Code / Failure Mode", "Occurrences"]
st.bar_chart(error_df.set_index("Error Code / Failure Mode"))

st.divider()

# Section 3: Interactive Inspector & Dependency Parser Visualizer
st.subheader("Interactive Inspector & Dependency Parse Audit Trail")

inspector_model = st.selectbox("Select Target Model", options=filtered_df["model"].unique())
model_samples = filtered_df[filtered_df["model"] == inspector_model]
selected_sample_id = st.selectbox("Select Sample ID to Inspect", options=model_samples["sample_id"].unique())
sample_data = model_samples[model_samples["sample_id"] == selected_sample_id].iloc[0]

inspect_col1, inspect_col2 = st.columns(2)

with inspect_col1:
    st.markdown(f"**Sample ID:** `{sample_data['sample_id']}`")
    st.markdown(f"**Target Model:** `{sample_data['model']}`")
    st.markdown(f"**Prompt Sent to LLM:**")
    st.info(sample_data["prompt"])
    st.markdown(f"**Raw Model Response:**")
    st.code(sample_data["raw_output"])
    status_color = "#1565c0" if sample_data["status"] == "CORRECT" else "#c62828"
    st.markdown(
        f"<p style='color: {status_color}; font-weight: 700;'>"
        f"Scored: {sample_data['status'].lower()}</p>",
        unsafe_allow_html=True,
    )

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