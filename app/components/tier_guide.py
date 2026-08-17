"""
Tier guide component — "How this works" expander for each application tier.

Renders a collapsible section with three tabs on the first page of every tier:
  1. Technical Flow   — libraries, data flow, architecture
  2. Workflow Steps   — what to do on each page
  3. Sample Output    — what results to expect

Usage (in any tier's first page):
    from components.tier_guide import render_tier_guide
    render_tier_guide("loan_ml")
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Guide content — one entry per tier ID
# ---------------------------------------------------------------------------

_GUIDES: dict[str, dict] = {

    # -----------------------------------------------------------------------
    "loan_ml": {
        "title": "T1 · Machine Learning",
        "flow_steps": [
            ("Upload CSV", "Raw loan dataset loaded into a pandas DataFrame. Columns auto-detected."),
            ("Explore", "Distribution plots, missing-value heatmap, class balance check, correlation matrix."),
            ("Preprocess", "sklearn Pipeline: median/mode imputation → StandardScaler / MinMaxScaler → OneHotEncoder. Fit on train only, transform both splits."),
            ("Train", "Four models: Logistic Regression, Decision Tree, Random Forest, XGBoost. Hyperparams configurable via sliders."),
            ("Evaluate", "Confusion matrix, ROC curve (AUC), precision/recall/F1. Side-by-side model comparison."),
            ("Download", "joblib-serialised model + preprocessor + metrics JSON. Combined bundle for deployment."),
        ],
        "workflow_steps": [
            "📤 **Upload Dataset** — upload any loan CSV (or use the sample). The app detects numeric/categorical columns automatically.",
            "📊 **Explore Data** — check distributions, missing values, and class balance before touching the model.",
            "🧹 **Preprocess** — pick your target column, scaling strategy, and imputation method. A fitted sklearn Pipeline is created.",
            "🤖 **Train Model** — choose a model (LR / DT / RF / XGBoost) and tune hyperparameters. Training takes 2–10 seconds.",
            "📈 **Evaluate** — inspect the confusion matrix, ROC curve, and feature importance. Compare multiple runs.",
            "⬇ **Download** — export the trained model, preprocessor, and metrics. Use the bundle for inference on new data.",
        ],
        "output": [
            ("Test accuracy", "Typically 80–90% on a balanced loan dataset."),
            ("ROC AUC", "0.85–0.95 for Random Forest / XGBoost. Closer to 1.0 = better."),
            ("Confusion matrix", "2×2 grid: True Positives, False Positives, False Negatives, True Negatives."),
            ("Feature importance", "Bar chart ranking which columns (credit score, income, DTI) most influence approval."),
            ("Download bundle", "loan_bundle.pkl — load with joblib.load(), call preprocessor.transform() then model.predict()."),
        ],
        "stack": ["scikit-learn", "XGBoost", "pandas", "plotly", "joblib"],
    },

    # -----------------------------------------------------------------------
    "loan_dl": {
        "title": "T2 · Deep Learning",
        "flow_steps": [
            ("Upload CSV", "Same raw dataset as T1 — identical upload and exploration flow."),
            ("Preprocess", "Same sklearn Pipeline as T1. Ensures fair comparison: only the model changes."),
            ("Train MLP", "sklearn MLPClassifier. Architecture (layers/neurons), activation function, solver, learning rate, and max epochs configurable."),
            ("Loss curve", "Training loss per epoch plotted in real time after training. Shows whether the network converged or overfit."),
            ("Evaluate", "Same metrics as T1 (accuracy, ROC AUC, confusion matrix) + epoch count and convergence status."),
            ("Compare vs T1", "Side-by-side accuracy and AUC against your saved T1 baseline to see if DL adds value."),
        ],
        "workflow_steps": [
            "📤 **Upload Dataset** — same CSV as T1 for a fair comparison.",
            "🧹 **Preprocess** — identical pipeline to T1. Feature engineering is not the variable here.",
            "🤖 **Train Model** — choose architecture depth (Shallow / Medium / Deep / Wide) and tune activation, solver, and epochs.",
            "📉 **Loss Curve** — watch the training loss drop. A flat curve means the network stopped learning; a rising validation loss means overfit.",
            "📈 **Evaluate** — compare accuracy and AUC against the T1 classical baseline.",
            "⬇ **Download** — export the MLP model and metrics.",
        ],
        "output": [
            ("Loss curve", "Descending curve = converging. Flat from epoch 1 = learning rate too low or data issue."),
            ("Test accuracy", "Similar to or slightly above T1 for tabular data. DL rarely dominates classical ML on small tables."),
            ("Epoch count", "How many epochs were needed before early stopping. Fewer = faster convergence."),
            ("vs T1 baseline", "Key takeaway: does the extra complexity of a neural network pay off for this dataset?"),
        ],
        "stack": ["scikit-learn MLPClassifier", "pandas", "plotly", "joblib"],
    },

    # -----------------------------------------------------------------------
    "loan_xai": {
        "title": "T3 · Explainability (XAI)",
        "flow_steps": [
            ("Upload & Train", "Same pipeline as T1. A model is trained first — XAI explains its predictions."),
            ("SHAP (global)", "SHAP (SHapley Additive exPlanations): each feature's average contribution across all predictions. Beeswarm plot + bar chart."),
            ("SHAP (local)", "For a single prediction: waterfall chart showing which features pushed the score up or down and by how much."),
            ("LIME (local)", "Independent cross-check using a local linear approximation. Confirms or challenges the SHAP finding."),
            ("Export", "SHAP values CSV (all rows), global importance CSV, per-instance LIME report CSV."),
        ],
        "workflow_steps": [
            "📤 **Upload Dataset** — same CSV. XAI requires a trained model, so the full T1 pipeline runs first.",
            "🧹 **Preprocess** — configure and fit the pipeline.",
            "🤖 **Train Model** — train any model. Tree models use TreeExplainer (fast); LR uses LinearExplainer; others use KernelExplainer (slow).",
            "🔍 **Explain** — three tabs: Global SHAP (all data), Local SHAP (one prediction), Local LIME (cross-check).",
            "⬇ **Download** — export SHAP values and importance rankings for your report or audit trail.",
        ],
        "output": [
            ("Beeswarm plot", "Each dot = one prediction. Right = pushed towards approval; left = pushed towards rejection. Colour = feature value."),
            ("Waterfall chart", "For applicant #N: shows the baseline probability and every feature's contribution step by step."),
            ("LIME bar chart", "Green bars = features supporting approval; red bars = features supporting rejection."),
            ("SHAP vs LIME", "If both agree on the top feature, the explanation is robust. If they disagree, investigate data quality."),
        ],
        "stack": ["SHAP", "LIME", "scikit-learn", "plotly"],
    },

    # -----------------------------------------------------------------------
    "loan_rag": {
        "title": "T4 · Retrieval-Augmented Generation (RAG)",
        "flow_steps": [
            ("Load PDF", "pypdf extracts text page by page. The full document text is stored in session state."),
            ("Chunk", "RecursiveCharacterTextSplitter splits text into overlapping chunks (configurable size/overlap). Overlap prevents missing context at boundaries."),
            ("Embed", "all-MiniLM-L6-v2 (HuggingFace) converts each chunk into a vector. ChromaDB EphemeralClient stores them in memory — no disk writes."),
            ("Query", "User question → embedded → cosine similarity search → top-k chunks retrieved → sent to LLM as context."),
            ("Generate", "meta-llama/llama-4-scout-17b-16e-instruct (via Groq) answers using ONLY the retrieved chunks. System prompt forbids hallucination — if it's not in the context, the LLM says so."),
        ],
        "workflow_steps": [
            "📄 **Load Policy** — click 'Load loan_policy.pdf' for the default FinCorp policy, or upload your own PDF/TXT.",
            "🔍 **Explore Chunks** — browse how the document was split. Use the search bar to find specific policy sections.",
            "⚙️ **Configure RAG** — tune chunk size (128–1024), overlap, embedding model, LLM model, and top-k retrieval. Then click 'Build vector store'.",
            "💬 **Chat** — ask any question about the policy. Sample questions are provided to get started.",
            "📜 **History** — review all Q&A pairs from the session.",
            "⬇ **Download** — export chat history (JSON/CSV), chunks, and config.",
        ],
        "output": [
            ("Answer", "Plain-English answer grounded in the policy. No hallucination — every claim is traceable to a chunk."),
            ("Source chunks", "Each answer shows the exact policy paragraphs used. Click to expand and verify."),
            ("Chat history", "All Q&A pairs with timestamps, exportable as JSON or CSV."),
            ("Reproducibility", "The Download page shows the exact Python code to recreate the session."),
        ],
        "stack": ["LangChain", "ChromaDB", "Groq (meta-llama/llama-4-scout-17b-16e-instruct)", "HuggingFace embeddings", "pypdf"],
    },

    # -----------------------------------------------------------------------
    "loan_agent": {
        "title": "T5 · AI Agent",
        "flow_steps": [
            ("Application form", "Applicant details and loan request captured as a structured dict."),
            ("validate_application", "Deterministic tool: checks age, income, employment, credit score against policy minimums. Returns PASSED or list of failures."),
            ("compute_risk_metrics", "Deterministic tool: calculates DTI ratio, estimates EMI, maps credit score to band, flags auto-decline conditions."),
            ("lookup_policy_rule", "Deterministic tool: retrieves embedded policy rules (auto-decline conditions, interest rate bands, eligibility thresholds)."),
            ("LLM synthesis", "meta-llama/llama-4-scout-17b-16e-instruct (via Groq) receives all three tool outputs and writes a structured APPROVED / DECLINED / MANUAL_REVIEW decision with reasoning."),
        ],
        "workflow_steps": [
            "📋 **Application** — fill the form or load a sample (Strong / Borderline / High-Risk applicant).",
            "🤖 **Run Agent** — click 'Evaluate with Agent'. Watch each tool call with its input and output.",
            "📄 **Decision** — structured report with decision banner, key metrics, and full agent reasoning.",
            "📜 **History** — all decisions evaluated in this session.",
            "⬇ **Download** — export decision JSON, history CSV, and a reproducibility code snippet.",
        ],
        "output": [
            ("Decision banner", "APPROVED (green) / DECLINED (red) / MANUAL_REVIEW (amber) with confidence."),
            ("Tool trace", "Step 1: validation result. Step 2: DTI, EMI, credit band. Step 3: policy rules consulted."),
            ("Agent reasoning", "LLM's written justification citing specific numbers from the tool outputs."),
            ("Conditions", "If approved: any conditions (e.g. 'collateral required', 'co-applicant needed')."),
        ],
        "stack": ["LangChain tools", "Groq (meta-llama/llama-4-scout-17b-16e-instruct)", "pandas"],
    },

    # -----------------------------------------------------------------------
    "loan_multi_agent": {
        "title": "T6 · Multi-Agent System",
        "flow_steps": [
            ("Application form", "Same structured input as T5."),
            ("LangGraph StateGraph", "Fan-out from START: Underwriter, Fraud Detector, and Compliance Officer start simultaneously."),
            ("Underwriter Agent", "Analyses financial affordability: DTI, EMI-to-income ratio, loan proportionality. Recommends APPROVE / DECLINE / REVIEW."),
            ("Fraud Detector Agent", "Looks for anomalies: income vs loan size, employment duration vs income level, age plausibility. Assigns risk level."),
            ("Compliance Officer Agent", "Checks all policy rules and auto-decline conditions. Flags regulatory non-compliance."),
            ("Supervisor Agent", "Fan-in: reads all three reports. Resolves disagreements using priority rules (Compliance DECLINE always overrides). Writes final consensus."),
        ],
        "workflow_steps": [
            "📋 **Application** — fill the form or load a sample. Try the Borderline applicant to see a split vote.",
            "🏛️ **Run Panel** — click 'Convene Credit Committee'. Three specialists run in parallel, then the Supervisor synthesises.",
            "📄 **Consensus** — see all three vote cards (Approve / Decline / Review) and the Supervisor's final ruling with reasoning.",
            "📜 **History** — all panel decisions with vote breakdowns (UW · FD · CO votes visible at a glance).",
            "⬇ **Download** — full panel report JSON with all specialist analyses and tool traces.",
        ],
        "output": [
            ("Three vote cards", "Underwriter 💼, Fraud Detector 🔎, Compliance Officer ⚖️ — each with their recommendation."),
            ("Consensus type", "UNANIMOUS (all agree) / MAJORITY / SPLIT — Supervisor explains which specialist's concern overrode the others."),
            ("Supervisor reasoning", "Why one specialist's DECLINE overrides another's APPROVE. Most interesting on split votes."),
            ("Vote history", "History table shows UW/FD/CO votes at a glance — easy to spot patterns across applicants."),
        ],
        "stack": ["LangGraph StateGraph", "Groq (meta-llama/llama-4-scout-17b-16e-instruct)", "parallel fan-out"],
    },
}


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

def render_tier_guide(tier_id: str) -> None:
    """Render the 'How this works' expander for the given tier.

    Args:
        tier_id: Application ID matching APPLICATIONS registry
                 (e.g. 'loan_ml', 'loan_rag', 'loan_agent').
    """
    guide = _GUIDES.get(tier_id)
    if not guide:
        return

    with st.expander("📖 How this works", expanded=False):
        tab_flow, tab_steps, tab_output = st.tabs([
            "🔧 Technical Flow",
            "📋 Workflow Steps",
            "📊 Sample Output",
        ])

        # ---- Technical Flow ---------------------------------------------
        with tab_flow:
            st.caption(f"**{guide['title']}** — data and execution path")
            for i, (step_name, step_desc) in enumerate(guide["flow_steps"], 1):
                col_num, col_content = st.columns([1, 11])
                with col_num:
                    st.markdown(
                        f"<div style='width:1.8rem;height:1.8rem;border-radius:50%;"
                        f"background:#6366f1;color:#fff;display:flex;align-items:center;"
                        f"justify-content:center;font-size:.7rem;font-weight:700;"
                        f"margin-top:.15rem;'>{i}</div>",
                        unsafe_allow_html=True,
                    )
                with col_content:
                    st.markdown(f"**{step_name}**")
                    st.caption(step_desc)

            st.markdown(
                "**Stack:** " + " · ".join(
                    f"`{s}`" for s in guide["stack"]
                )
            )

        # ---- Workflow Steps ---------------------------------------------
        with tab_steps:
            st.caption("Follow these steps in order. Each page unlocks the next.")
            for i, step in enumerate(guide["workflow_steps"], 1):
                st.markdown(f"{i}. {step}")

        # ---- Sample Output ----------------------------------------------
        with tab_output:
            st.caption("What you will see after completing the workflow.")
            for label, description in guide["output"]:
                col_label, col_desc = st.columns([3, 7])
                with col_label:
                    st.markdown(
                        f"<div style='font-size:.78rem;font-weight:700;"
                        f"color:#4f46e5;padding-top:.1rem;'>{label}</div>",
                        unsafe_allow_html=True,
                    )
                with col_desc:
                    st.caption(description)
                st.divider()
