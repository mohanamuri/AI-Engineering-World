"""
Documentation page — single reference for the entire AI Engineering World platform.

Covers: architecture, tech stack, tier guide, integrations, API curl commands, and sample data.
"""

import streamlit as st

_BASE = "https://ai-engineering-world.onrender.com"
_SWAGGER = f"{_BASE}/docs"


def render() -> None:
    st.title("📖 Platform Documentation")
    st.caption("One-place reference — architecture, tech stack, integrations, and live API commands.")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏛 Architecture",
        "⚙ Tech Stack",
        "🎯 Tier Guide",
        "🔗 Integrations",
        "🔌 API & curl",
        "🗂 Sample Data",
    ])

    with tab1:
        _architecture()
    with tab2:
        _tech_stack()
    with tab3:
        _tier_guide()
    with tab4:
        _integrations()
    with tab5:
        _api_curl()
    with tab6:
        _sample_data()


# ─── Tab 1 — Architecture ─────────────────────────────────────────────────────

def _architecture() -> None:
    st.subheader("Platform Architecture")
    st.write(
        "AI Engineering World is a full-stack ML portfolio demonstrating six capability tiers "
        "across two business domains (Loan Eligibility and HR Analytics). "
        "The same service layer powers both the Streamlit UI and the FastAPI REST endpoints."
    )

    st.graphviz_chart("""
    digraph platform {
        rankdir=TB
        node [shape=box style=filled fontname="Helvetica" fontsize=11]
        edge [fontsize=10]

        User [label="User / Browser" fillcolor="#E8F4FD" shape=ellipse]

        subgraph cluster_ui {
            label="Streamlit Cloud  (streamlit.app)"
            style=filled fillcolor="#F0F8FF"
            UI [label="Streamlit UI\\n12 Apps  |  Dashboard" fillcolor="#BDD7EE"]
        }

        subgraph cluster_api {
            label="Render  (onrender.com)"
            style=filled fillcolor="#F0FFF0"
            API [label="FastAPI REST\\n10 Routers  |  /docs" fillcolor="#C6EFCE"]
        }

        subgraph cluster_services {
            label="Service Layer  (shared by UI + API)"
            style=filled fillcolor="#FFFBF0"
            SVC [label="ML · DL · XAI · RAG · Agent · Multi-Agent\\nscikit-learn  |  MLPClassifier  |  SHAP  |  LIME\\nLangChain  |  LangGraph  |  ChromaDB" fillcolor="#FFEB9C"]
        }

        subgraph cluster_ext {
            label="External Services"
            style=filled fillcolor="#FFF0F0"
            Groq [label="Groq API\\nllama-3.1-8b-instant" fillcolor="#FFC7CE"]
            GitHub [label="GitHub\\nSource of truth" fillcolor="#FFC7CE"]
        }

        User -> UI [label="browser"]
        User -> API [label="REST / curl"]
        UI -> SVC [label="direct import"]
        API -> SVC [label="direct import"]
        SVC -> Groq [label="T4-T6 LLM calls"]
        GitHub -> UI [label="auto-deploy"]
        GitHub -> API [label="auto-deploy"]
    }
    """)

    st.subheader("Key Design Decisions")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Shared service layer**\n\nUI and API import the same Python services — no code duplication, one place to fix bugs.")
    with col2:
        st.info("**Session-based API**\n\nEach pipeline run gets a UUID session. State flows upload → preprocess → train → evaluate without re-uploading data.")
    with col3:
        st.info("**Tier progression**\n\nT1→T6 is intentional: each tier adds one capability (ML → DL → XAI → RAG → Agent → Multi-Agent).")


# ─── Tab 2 — Tech Stack ───────────────────────────────────────────────────────

def _tech_stack() -> None:
    st.subheader("Tech Stack")

    st.markdown("#### Frontend / UI")
    st.table({
        "Technology": ["Streamlit", "Streamlit Cloud"],
        "Version": ["≥ 1.35", "Hosted"],
        "Purpose": ["Interactive UI, session state, charts", "Free hosting, auto-deploy from GitHub main"],
    })

    st.markdown("#### Backend / API")
    st.table({
        "Technology": ["FastAPI", "Uvicorn", "Pydantic", "Render"],
        "Version": ["≥ 0.115", "≥ 0.29", "v2", "Free tier"],
        "Purpose": ["REST framework, OpenAPI/Swagger auto-docs", "ASGI server", "Request/response validation", "API hosting, auto-deploy from GitHub main"],
    })

    st.markdown("#### ML / DL / XAI (Tiers 1–3)")
    st.table({
        "Technology": ["scikit-learn", "XGBoost", "SHAP", "LIME", "pandas / numpy", "joblib"],
        "Version": ["≥ 1.5", "≥ 2.0", "0.52", "≥ 0.2", "≥ 2.0 / ≥ 1.26", "≥ 1.4"],
        "Purpose": [
            "Logistic Regression, Decision Tree, Random Forest, MLP",
            "Gradient boosted trees classifier",
            "Global feature importance (TreeExplainer / LinearExplainer)",
            "Local instance explanations",
            "Data wrangling",
            "Model serialization (.pkl bundle)",
        ],
    })

    st.markdown("#### LLM / RAG / Agent (Tiers 4–6)")
    st.table({
        "Technology": ["LangChain", "LangGraph", "ChromaDB", "sentence-transformers", "Groq API", "pypdf"],
        "Version": ["≥ 0.3", "≥ 0.2", "≥ 0.5", "≥ 3.0", "REST", "≥ 4.0"],
        "Purpose": [
            "RAG pipeline, prompt templates, chat models",
            "Agent graphs: ReAct (T5), StateGraph fan-out (T6)",
            "In-memory vector store for document Q&A",
            "all-MiniLM-L6-v2 local embeddings (Streamlit only)",
            "LLM inference — llama-3.1-8b-instant, free tier",
            "PDF document parsing for RAG",
        ],
    })

    st.markdown("#### Infrastructure")
    st.table({
        "Technology": ["GitHub", "Streamlit Cloud", "Render"],
        "Role": ["Source of truth", "UI deployment", "API deployment"],
        "Trigger": ["Push to main", "Auto-deploy on push to main", "Auto-deploy on push to main"],
    })


# ─── Tab 3 — Tier Guide ───────────────────────────────────────────────────────

def _tier_guide() -> None:
    st.subheader("Tier-by-Tier Breakdown")
    st.write("Each tier adds one capability on top of the previous. Both Loan and HR domains follow the same six-tier pattern.")

    tiers = [
        {
            "tier": "T1 — Machine Learning",
            "icon": "🤖",
            "what": "Train and evaluate classical ML classifiers on tabular data.",
            "models": "Logistic Regression, Decision Tree, Random Forest, XGBoost",
            "pipeline": "Upload CSV → Explore → Preprocess → Train → Evaluate → Predict → Download bundle",
            "key_concept": "Preprocessing pipeline fitted on train split only (no data leakage). Model + pipeline saved together as a .pkl bundle.",
            "services": "data_loader, exploration, preprocessor, trainer, metrics",
        },
        {
            "tier": "T2 — Deep Learning",
            "icon": "🧠",
            "what": "Replace the classical classifier with a Multi-Layer Perceptron (MLP).",
            "models": "MLPClassifier — Small [64], Medium [128→64], Large [256→128→64], Wide [512→256]",
            "pipeline": "Same as T1 + architecture selector, loss curve visualization",
            "key_concept": "sklearn MLPClassifier — same preprocessing as T1, easier to compare DL vs ML on identical data.",
            "services": "loan_dl/services/trainer (DLTrainResult, loss_curve)",
        },
        {
            "tier": "T3 — Explainable AI",
            "icon": "🔍",
            "what": "Explain why the model made a specific prediction.",
            "models": "SHAP (global) + LIME (local) on top of any T1 model",
            "pipeline": "T1 pipeline → Explain (SHAP global importance + LIME instance explanation)",
            "key_concept": "SHAP uses TreeExplainer for tree models (fast), LinearExplainer for LR. LIME perturbs the input and fits a local linear model.",
            "services": "loan_xai/services/explainer (build_explanation, explain_instance_lime)",
        },
        {
            "tier": "T4 — RAG",
            "icon": "📚",
            "what": "Answer questions grounded in uploaded policy documents.",
            "models": "all-MiniLM-L6-v2 embeddings + Groq llama-3.1-8b-instant",
            "pipeline": "Upload PDF/TXT → Configure (chunk + embed → ChromaDB) → Chat → History",
            "key_concept": "Retrieval-Augmented Generation: retrieve top-k relevant chunks first, then generate answer from context only. Prevents hallucination.",
            "services": "document_loader, vector_store (ChromaDB EphemeralClient), rag_chain",
        },
        {
            "tier": "T5 — AI Agent",
            "icon": "🤖",
            "what": "Automated decision pipeline: deterministic tools + LLM synthesis.",
            "models": "3 deterministic tools → Groq LLM for final decision narrative",
            "pipeline": "Submit application → validate → compute_risk → lookup_policy → LLM synthesis → APPROVED / DECLINED / MANUAL_REVIEW",
            "key_concept": "Tools always run in fixed order (no hallucinated tool calls). LLM only writes the decision letter — ground-truth numbers come from tools.",
            "services": "agent_tools (3 @tool functions), agent_graph (run_agent → AgentRunResult)",
        },
        {
            "tier": "T6 — Multi-Agent",
            "icon": "👥",
            "what": "Three independent specialist agents + supervisor consensus via LangGraph.",
            "models": "3 specialist LLMs in parallel → 1 supervisor LLM (4 Groq calls total)",
            "pipeline": "Submit → [Underwriter ‖ Fraud Detector ‖ Compliance] → Supervisor → final decision",
            "key_concept": "Fan-out / fan-in StateGraph. Specialists may disagree — supervisor resolves with priority rules (Compliance > Fraud > Underwriter).",
            "services": "specialist_agents (3 run_* functions), panel_graph (LangGraph StateGraph, run_panel → PanelRunResult)",
        },
    ]

    for t in tiers:
        with st.expander(f"{t['icon']}  {t['tier']}", expanded=False):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**What it does:** {t['what']}")
                st.markdown(f"**Models / Methods:** {t['models']}")
                st.markdown(f"**Pipeline:** `{t['pipeline']}`")
            with col2:
                st.info(f"**Key concept:** {t['key_concept']}")
                st.caption(f"**Services layer:** `{t['services']}`")


# ─── Tab 4 — Integrations ─────────────────────────────────────────────────────

def _integrations() -> None:
    st.subheader("Integration Map")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Groq API")
        st.write(
            "Used by T4 (RAG), T5 (Agent), T6 (Multi-Agent) for LLM inference. "
            "Model: `llama-3.1-8b-instant` — fast, free tier."
        )
        st.markdown("""
**Streamlit:** key from `st.secrets["GROQ_API_KEY"]` (set in Streamlit Cloud dashboard)

**FastAPI:** key from `os.environ["GROQ_API_KEY"]` (set in Render Environment tab)

**How the services stay compatible:**
```python
def _get_groq_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")
```
The `import streamlit` is inside the `try` block so it fails silently on Render (no Streamlit installed there).
        """)

        st.markdown("#### Render (FastAPI)")
        st.write("Free-tier web service. Deploys from the `main` branch automatically.")
        st.markdown("""
| Setting | Value |
|---|---|
| Build command | `pip install -r requirements-api.txt` |
| Start command | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| Branch | `main` |
| Env var | `GROQ_API_KEY` |

**Limitation:** 512 MB RAM — sentence-transformers/PyTorch excluded. RAG endpoints available in Streamlit UI only.
        """)

    with col2:
        st.markdown("#### Streamlit Cloud")
        st.write("Free hosting for the Streamlit UI. Auto-deploys when `main` branch is updated.")
        st.markdown("""
| Setting | Value |
|---|---|
| Entry point | `main.py` |
| Branch | `main` |
| Secrets | `GROQ_API_KEY = "..."` |
| Requirements | `requirements.txt` (full deps including torch) |
        """)

        st.markdown("#### GitHub")
        st.write("Source of truth. Both Streamlit Cloud and Render auto-deploy from `main`.")
        st.markdown("""
**Branching strategy:**
- `dev` — active development
- `main` — production (triggers deploys on both platforms)

**Workflow:**
```bash
git push origin dev
git checkout main
git merge dev
git push origin main  # triggers both deploys
git checkout dev
```
        """)

    st.divider()
    st.markdown("#### Data Flow — Session-based API Pipeline")
    st.graphviz_chart("""
    digraph session {
        rankdir=LR
        node [shape=box style=filled fillcolor="#BDD7EE" fontsize=11]

        Upload [label="POST /upload\\nCSV → session_id"]
        Explore [label="GET /explore\\nprofile dataset"]
        Preprocess [label="POST /preprocess\\nfit pipeline"]
        Train [label="POST /train\\nfit model"]
        Evaluate [label="GET /evaluate\\nmetrics"]
        Predict [label="POST /predict\\nraw features → label"]
        Download [label="GET /download/bundle\\nmodel + pipeline .pkl"]

        Upload -> Explore -> Preprocess -> Train -> Evaluate -> Predict -> Download
    }
    """)


# ─── Tab 5 — API & curl ───────────────────────────────────────────────────────

def _api_curl() -> None:
    st.subheader("Live API Reference")
    st.markdown(
        f"**Swagger UI:** [`{_SWAGGER}`]({_SWAGGER})  — interactive docs with Try It Out for every endpoint."
    )
    st.info("Render free tier spins down after 15 min inactivity. First request may take 30–50 s to wake up.")

    st.markdown("---")
    st.markdown("#### Tier 1–3: Quick checks (no file needed)")
    st.code(f"""# Loan ML / HR ML — list models
curl {_BASE}/api/loan-ml/models
curl {_BASE}/api/hr-ml/models

# Loan DL / HR DL — list architectures
curl {_BASE}/api/loan-dl/architectures
curl {_BASE}/api/hr-dl/architectures

# Loan XAI / HR XAI — list models
curl {_BASE}/api/loan-xai/models
curl {_BASE}/api/hr-xai/models""", language="bash")

    st.markdown("---")
    st.markdown("#### Tier 5: Loan Agent — full run")
    st.code(f"""# Step 1 — create session
SESSION=$(curl -s -X POST {_BASE}/api/loan-agent/session \\
  | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

# Step 2 — run agent (calls validate → risk metrics → policy → Groq LLM)
curl -X POST {_BASE}/api/loan-agent/$SESSION/run \\
  -H "Content-Type: application/json" \\
  -d '{{
    "application": {{
      "applicant_name": "Jane Smith",
      "age": 35,
      "annual_income": 75000,
      "loan_amount": 250000,
      "credit_score": 720,
      "employment_status": "Employed",
      "employment_months": 48,
      "existing_debt": 15000,
      "loan_purpose": "Home"
    }}
  }}'

# Step 3 — history
curl {_BASE}/api/loan-agent/$SESSION/history""", language="bash")

    st.markdown("#### Tier 5: HR Agent — full run")
    st.code(f"""SESSION=$(curl -s -X POST {_BASE}/api/hr-agent/session \\
  | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

curl -X POST {_BASE}/api/hr-agent/$SESSION/run \\
  -H "Content-Type: application/json" \\
  -d '{{
    "employee": {{
      "Age": 32, "Department": "Sales", "JobRole": "Sales Representative",
      "JobSatisfaction": 2, "EnvironmentSatisfaction": 2, "WorkLifeBalance": 1,
      "OverTime": "Yes", "YearsAtCompany": 2, "YearsSinceLastPromotion": 2,
      "MonthlyIncome": 3500, "NumCompaniesWorked": 4, "TotalWorkingYears": 6
    }}
  }}'""", language="bash")

    st.markdown("---")
    st.markdown("#### Tier 6: Loan Multi-Agent — panel run")
    st.code(f"""SESSION=$(curl -s -X POST {_BASE}/api/loan-multi-agent/session \\
  | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

# Runs: Underwriter ‖ Fraud Detector ‖ Compliance → Supervisor (4 Groq calls)
curl -X POST {_BASE}/api/loan-multi-agent/$SESSION/panel \\
  -H "Content-Type: application/json" \\
  -d '{{
    "application": {{
      "applicant_name": "John Doe",
      "age": 28, "annual_income": 45000, "loan_amount": 300000,
      "credit_score": 590, "employment_status": "Employed",
      "employment_months": 12, "existing_debt": 25000, "loan_purpose": "Home"
    }}
  }}'""", language="bash")

    st.markdown("#### Tier 6: HR Multi-Agent — panel run")
    st.code(f"""SESSION=$(curl -s -X POST {_BASE}/api/hr-multi-agent/session \\
  | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

# Runs: HR Manager ‖ Perf Evaluator ‖ Risk Assessor → HR Director (4 Groq calls)
curl -X POST {_BASE}/api/hr-multi-agent/$SESSION/panel \\
  -H "Content-Type: application/json" \\
  -d '{{
    "employee": {{
      "Age": 29, "Department": "Sales", "JobRole": "Sales Representative",
      "JobSatisfaction": 1, "EnvironmentSatisfaction": 1, "WorkLifeBalance": 1,
      "OverTime": "Yes", "YearsAtCompany": 1, "YearsSinceLastPromotion": 1,
      "MonthlyIncome": 2800, "NumCompaniesWorked": 5, "TotalWorkingYears": 5
    }}
  }}'""", language="bash")

    st.markdown("---")
    st.markdown("#### Notes")
    st.markdown("""
- **RAG endpoints** (`/api/loan-rag`, `/api/hr-rag`) are **not exposed** on Render — sentence-transformers/PyTorch exceeds the free tier 512 MB RAM limit. Use the Streamlit UI for RAG.
- **Agent/Multi-Agent** calls hit Groq — expect **10–20 s** response on warm instance, up to **50 s** on cold start.
- **Session IDs** are in-memory only — they reset when Render restarts the service.
- All endpoints documented interactively at [`/docs`]({_SWAGGER}).
    """)


# ─── Tab 6 — Sample Data ──────────────────────────────────────────────────────

def _sample_data() -> None:
    st.subheader("Sample Data Files")
    st.write(
        "All sample files live in the `data/` directory of the repository. "
        "Use them for demos, testing, and showcasing. Every app works out-of-the-box with its paired file."
    )

    # ── Domain Projects ──────────────────────────────────────────────────────
    st.markdown("#### Domain Projects — CSV Datasets")
    st.info(
        "Upload these CSV files in the **Upload** step of any ML / DL / XAI tier. "
        "The pipeline auto-detects the target column."
    )
    st.table({
        "File": [
            "data/loan_eligibility_sample.csv",
            "data/hr_attrition_sample.csv",
        ],
        "Rows": ["500", "400"],
        "Target column": ["LoanApproved  (0 / 1)", "Attrition  (Yes / No)"],
        "Key features": [
            "Age, AnnualIncome, LoanAmount, CreditScore, EmploymentStatus, ExistingDebt, LoanPurpose",
            "JobSatisfaction, OverTime, MonthlyIncome, YearsAtCompany, WorkLifeBalance, Department",
        ],
        "Used by": [
            "Loan Eligibility — T1 ML, T2 DL, T3 XAI",
            "HR Analytics — T1 ML, T2 DL, T3 XAI",
        ],
    })

    st.divider()

    # ── RAG — Policy documents ────────────────────────────────────────────────
    st.markdown("#### RAG — Policy Documents")
    st.info(
        "Upload these files in the **Load Policy** step of any RAG tier, "
        "or use all three together in **RAG Projects → UC1 Multi-Document RAG**."
    )
    st.table({
        "File": [
            "data/loan_policy.pdf",
            "data/hr_policy.txt",
            "data/rag_sample_docs/remote_work_policy.txt",
            "data/rag_sample_docs/employee_benefits_guide.txt",
            "data/rag_sample_docs/code_of_conduct.txt",
        ],
        "Format": ["PDF", "TXT", "TXT", "TXT", "TXT"],
        "Content": [
            "FinCorp Bank loan eligibility and credit policy",
            "HR attrition, retention, and performance management policy",
            "Remote work eligibility, equipment, security, and expenses",
            "Health insurance, 401k, PTO, parental leave, wellness budget",
            "Conflicts of interest, gifts, anti-bribery, harassment, reporting",
        ],
        "Used by": [
            "Loan RAG (T4)",
            "HR RAG (T4)",
            "RAG Projects UC1 (multi-doc demo)",
            "RAG Projects UC1 (multi-doc demo)",
            "RAG Projects UC1 (multi-doc demo)",
        ],
    })

    st.divider()

    # ── Demo script ───────────────────────────────────────────────────────────
    st.markdown("#### Demo Script — Multi-Document RAG (UC1)")
    st.write("For a live showcase of UC1, upload all three `rag_sample_docs/` files together, then try these questions:")
    st.markdown("""
| Question | Why it's a good demo |
|---|---|
| *"What is the monthly internet allowance for remote workers?"* | Answer is in Benefits Guide — shows single-doc retrieval |
| *"What happens if an employee violates the remote work security rules?"* | Spans Remote Work Policy + Code of Conduct — shows cross-doc retrieval |
| *"Summarise the key employee obligations across all three documents."* | Forces the LLM to synthesise from all 3 docs |
| *"What is the gift limit for external parties and what happens if it's exceeded?"* | Code of Conduct answer — shows exact-term retrieval |
| *"How many paid parental leave weeks does a primary caregiver receive?"* | Benefits Guide — tests specific numeric fact retrieval |
    """)

    st.divider()

    # ── Agent / Multi-Agent ───────────────────────────────────────────────────
    st.markdown("#### Agent & Multi-Agent — No file upload needed")
    st.write(
        "T5 (Agent) and T6 (Multi-Agent) take structured form input directly in the UI — "
        "no file to upload. Use the values below for a quick demo run."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Loan Agent / Multi-Agent — approve scenario**")
        st.code("""{
  "age": 35,
  "annual_income": 85000,
  "loan_amount": 200000,
  "credit_score": 740,
  "employment_status": "Employed",
  "employment_months": 60,
  "existing_debt": 12000,
  "loan_purpose": "Home"
}""", language="json")
        st.caption("Expected: APPROVED — strong credit, low DTI")

        st.markdown("**Loan Agent / Multi-Agent — decline scenario**")
        st.code("""{
  "age": 24,
  "annual_income": 28000,
  "loan_amount": 350000,
  "credit_score": 530,
  "employment_status": "Part-Time",
  "employment_months": 4,
  "existing_debt": 18000,
  "loan_purpose": "Personal"
}""", language="json")
        st.caption("Expected: DECLINED — poor credit, high DTI, short tenure")

    with col2:
        st.markdown("**HR Agent / Multi-Agent — low risk scenario**")
        st.code("""{
  "Age": 42,
  "Department": "Research & Development",
  "JobRole": "Research Director",
  "JobSatisfaction": 4,
  "EnvironmentSatisfaction": 4,
  "WorkLifeBalance": 3,
  "OverTime": "No",
  "YearsAtCompany": 12,
  "YearsSinceLastPromotion": 1,
  "MonthlyIncome": 15000,
  "NumCompaniesWorked": 2,
  "TotalWorkingYears": 18
}""", language="json")
        st.caption("Expected: LOW RISK — senior, satisfied, tenured")

        st.markdown("**HR Agent / Multi-Agent — high risk scenario**")
        st.code("""{
  "Age": 26,
  "Department": "Sales",
  "JobRole": "Sales Representative",
  "JobSatisfaction": 1,
  "EnvironmentSatisfaction": 1,
  "WorkLifeBalance": 1,
  "OverTime": "Yes",
  "YearsAtCompany": 1,
  "YearsSinceLastPromotion": 1,
  "MonthlyIncome": 2800,
  "NumCompaniesWorked": 5,
  "TotalWorkingYears": 4
}""", language="json")
        st.caption("Expected: HIGH RISK — low satisfaction, overtime, short tenure")
