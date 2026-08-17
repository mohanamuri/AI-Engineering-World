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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏛 Architecture",
        "⚙ Tech Stack",
        "🎯 Tier Guide",
        "🔗 Integrations",
        "🔌 API & curl",
        "🗂 Sample Data",
        "📚 Glossary",
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
    with tab7:
        _glossary()


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
            Groq [label="Groq API\\nmeta-llama/llama-4-scout-17b-16e-instruct" fillcolor="#FFC7CE"]
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
            "LLM inference — meta-llama/llama-4-scout-17b-16e-instruct, free tier",
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
            "models": "all-MiniLM-L6-v2 embeddings + Groq meta-llama/llama-4-scout-17b-16e-instruct",
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

    st.divider()
    st.subheader("RAG Patterns — Coverage Map")
    st.write("The RAG Projects section covers seven progressively advanced retrieval patterns.")
    st.table({
        "Type": [
            "Multi-Document RAG",
            "Hybrid Search RAG",
            "Agentic RAG",
            "Self-RAG",
            "GraphRAG",
            "Corrective RAG (CRAG)",
            "Modular RAG",
        ],
        "What it does": [
            "Multiple docs embedded into a single vector store; every answer cites its source document",
            "BM25 keyword search + dense vector search fused via Reciprocal Rank Fusion (RRF)",
            "Agent decides whether to retrieve, reformulates query if context is weak, iterates",
            "Generates answer then self-critiques on Groundedness, Relevance, Completeness; rewrites on low scores",
            "Extracts a knowledge graph (entities + relationships) from docs; retrieves via graph traversal + vector search",
            "Grades each retrieved document for relevance; falls back to web search if context is insufficient",
            "Composable pipeline with swappable retriever, reranker, and generator components",
        ],
        "Status": [
            "✅ UC1 — live",
            "✅ UC2 — live",
            "✅ UC3 — live",
            "✅ UC4 — live",
            "✅ UC5 — live",
            "✅ UC6 — live",
            "✅ UC7 — live",
        ],
    })

    st.divider()
    st.subheader("Agent Patterns — Coverage Map")
    st.write("The Agent Projects section covers four standalone LangGraph agent architectures.")
    st.table({
        "Pattern": [
            "ReAct Agent",
            "Plan-and-Execute",
            "Reflection Agent",
            "Multi-Agent Supervisor",
        ],
        "What it does": [
            "Reason+Act loop — LLM reasons, calls a tool, observes, reasons again until it can answer",
            "Planner creates a multi-step plan upfront; executor runs each step; responder synthesises",
            "Generator writes draft; critic scores Clarity/Accuracy/Completeness; reviser rewrites on low scores",
            "Supervisor routes sub-tasks to specialist agents (Researcher, Analyst, Writer); Writer is terminal",
        ],
        "Status": [
            "✅ UC1 — live",
            "✅ UC2 — live",
            "✅ UC3 — live",
            "✅ UC4 — live",
        ],
    })

    st.divider()
    st.subheader("MAS Patterns — Coverage Map")
    st.write("The Multi-Agent Projects section covers four progressively advanced multi-agent coordination patterns.")
    st.table({
        "UC": ["UC1", "UC2", "UC3", "UC4"],
        "Pattern": [
            "Supervisor Pipeline",
            "Parallel Agents",
            "Debate & Judge",
            "Research Team",
        ],
        "Agents": [
            "Collector → Processor → Writer → Supervisor",
            "Facts + Critic + Creative → Aggregator",
            "Proponent ↔ Opponent → Judge",
            "Planner → Researcher × N → Analyst → Writer",
        ],
        "Key concept": [
            "Fixed sequential pipeline — each agent receives the previous agent's output (chained context)",
            "Fan-out / Fan-in — three independent agents, no shared state, merged by Aggregator",
            "Adversarial pattern — opposing agents surface trade-offs; neutral Judge arbitrates",
            "Iterative research loop — Researcher called once per question; memory accumulates across all stages",
        ],
        "Status": [
            "✅ UC1 — live",
            "✅ UC2 — live",
            "✅ UC3 — live",
            "✅ UC4 — live",
        ],
    })

    st.divider()
    st.subheader("Media Intelligence Patterns — Coverage Map")
    st.write("The Media Projects section covers four multimodal AI use cases — audio, video, image, and document — all powered by Groq free-tier APIs (Whisper + Vision).")
    st.table({
        "UC": ["UC1", "UC2", "UC3", "UC4"],
        "Name": [
            "Meeting Intelligence",
            "Video Intelligence",
            "Image Intelligence",
            "Document Scanner",
        ],
        "Input": [
            ".mp3 / .wav / .m4a",
            ".mp4 / .mov",
            ".jpg / .png",
            "Photo of doc / whiteboard / slide",
        ],
        "Pipeline": [
            "Groq Whisper → transcript → LLM extracts summary, decisions, action items, sentiment",
            "ffmpeg audio extraction → Groq Whisper → transcript → same structured report as UC1",
            "Groq Vision (llama-4-scout-17b) → describe scene, extract embedded text, answer questions",
            "Groq Vision (llama-4-scout-17b) → structured extraction → export JSON / plain text",
        ],
        "Key concept": [
            "Speech-to-text + LLM structured extraction — one audio file produces a complete meeting report",
            "Video-to-audio demux (ffmpeg) feeds the same Whisper + LLM pipeline as Meeting Intelligence",
            "Vision-language model processes raw image pixels — no OCR pre-step required",
            "Vision LLM turns a photo of any document into machine-readable structured data",
        ],
        "Status": [
            "✅ UC1 — live",
            "✅ UC2 — live",
            "✅ UC3 — live",
            "✅ UC4 — live",
        ],
    })

    st.divider()
    st.subheader("AI Optimisation Techniques — Coverage Map")
    st.write(
        "Four production LLM optimisation patterns — each UC solves one distinct concern "
        "and answers one of the most common LLM system design interview questions."
    )
    st.table({
        "UC": ["UC1", "UC2", "UC3", "UC4"],
        "Technique": [
            "Semantic Caching",
            "Model Routing",
            "Memory Patterns",
            "Streaming + Fallback",
        ],
        "Concern": [
            "Cost",
            "Cost + Performance",
            "Memory",
            "Performance + Reliability",
        ],
        "Key interview question it answers": [
            '"How do you reduce LLM API costs in production?"',
            '"How do you scale LLM systems without costs exploding?"',
            '"How do LLMs maintain context across conversations?"',
            '"How do you make LLM responses feel fast? What if the API goes down?"',
        ],
        "Status": [
            "✅ UC1 — live",
            "✅ UC2 — live",
            "✅ UC3 — live",
            "✅ UC4 — live",
        ],
    })

    st.markdown("##### What each UC teaches")

    aiopt_details = [
        (
            "UC1 — Semantic Caching",
            "- **Problem:** Every LLM call costs money. Users ask semantically identical questions in different words.\n"
            "- **Solution:** Embed each query into a vector. On cache hit (cosine similarity ≥ threshold), return the stored response instantly — no LLM call.\n"
            "- **Shows:** Latency comparison (cached ~5 ms vs uncached ~800 ms), cache hit rate, cost savings per query.\n"
            "- **Stack:** `sentence-transformers` (all-MiniLM-L6-v2) · NumPy cosine similarity · Groq meta-llama/llama-4-scout-17b-16e-instruct",
        ),
        (
            "UC2 — Model Routing",
            "- **Problem:** A 70B model is 5–10× more expensive than an 8B model. Most queries don't need it.\n"
            "- **Solution:** A lightweight classifier (one 8B call, max 5 tokens) labels each query SIMPLE or COMPLEX. Simple → 8B; Complex → 70B.\n"
            "- **Shows:** Routing decision trace, latency difference per model, estimated cost difference.\n"
            "- **Stack:** Groq meta-llama/llama-4-scout-17b-16e-instruct (classifier + simple model) · meta-llama/llama-4-maverick-17b-128e-instruct (complex model)",
        ),
        (
            "UC3 — Memory Patterns",
            "- **Problem:** LLMs are stateless. Long conversations exceed the context limit or cost too much to resend in full.\n"
            "- **Buffer Memory:** Keep the last N messages verbatim — simple, hits context limit on long sessions.\n"
            "- **Summary Memory:** Summarise old turns with an LLM call; keep summary + recent 4 messages — scalable.\n"
            "- **Entity Memory:** Extract named entities each turn; inject a fact store into the system prompt — best for assistants that remember the user.\n"
            "- **Shows:** Side-by-side comparison of all 3 strategies on a multi-turn conversation.",
        ),
        (
            "UC4 — Streaming + Fallback",
            "- **Streaming:** Tokens appear as they are generated → perceived latency drops 70–90 %. Total time is the same; the user just sees output immediately.\n"
            "- **Fallback:** Primary model fails or rate-limits → retry with exponential backoff → automatically switch to backup model.\n"
            "- **Shows:** Streaming vs blocking side-by-side, fallback trigger demo with force-fail flag.\n"
            "- **Stack:** Groq `stream=True` · `st.write_stream()` · retry backoff · meta-llama/llama-4-maverick-17b-128e-instruct as fallback",
        ),
    ]

    for title, body in aiopt_details:
        with st.expander(title, expanded=False):
            st.markdown(body)

    st.markdown("##### How all four patterns work together in production")
    st.code(
        "User query\n"
        "    ↓\n"
        "[UC1] Semantic Cache  → HIT? Return instantly (no LLM needed)\n"
        "    ↓ MISS\n"
        "[UC2] Model Router    → Simple? Use 8B (cheap). Complex? Use 70B (powerful).\n"
        "    ↓\n"
        "[UC3] Memory          → Inject the right conversation context\n"
        "    ↓\n"
        "[UC4] Streaming       → Stream tokens to the user as they arrive\n"
        "      Fallback        → If primary fails, retry → switch model automatically\n\n"
        "Result: ~60–80 % lower API cost · ~70–90 % lower perceived latency · near-100 % uptime",
        language="text",
    )

    st.divider()
    st.subheader("LLM Evaluation — Coverage Map")
    st.write(
        "Four systematic techniques for measuring LLM and RAG output quality. "
        "All metrics are implemented via LLM prompts — no paid evaluation library required."
    )
    st.table({
        "UC": ["UC1", "UC2", "UC3", "UC4"],
        "Technique": [
            "RAGAS Evaluation",
            "LLM-as-Judge",
            "Hallucination Detection",
            "Eval Pipeline",
        ],
        "What it measures": [
            "Faithfulness · Answer Relevance · Context Recall · Context Precision",
            "Accuracy · Relevance · Clarity · Completeness · Conciseness (1–10 each)",
            "Individual claims → SUPPORTED / CONTRADICTED / UNVERIFIABLE",
            "Full test dataset → all metrics → pass/fail dashboard",
        ],
        "LLM calls": [
            "4 per evaluation (one per metric)",
            "5 per response (one per criterion)",
            "1 (claim extraction) + N (one per claim)",
            "Batch of RAGAS + hallucination calls",
        ],
        "Status": [
            "✅ UC1 — live",
            "✅ UC2 — live",
            "✅ UC3 — live",
            "✅ UC4 — live",
        ],
    })

    st.markdown("##### What each UC teaches")
    llmeval_details = [
        (
            "UC1 — RAGAS Evaluation",
            "- **Problem:** RAG systems have no automated quality measure — how do you know if your RAG app gives good answers?\n"
            "- **Faithfulness (0–1):** Is every claim in the answer supported by the retrieved context? Low score = hallucination risk.\n"
            "- **Answer Relevance (0–1):** Does the answer actually address the question asked?\n"
            "- **Context Recall (0–1):** Did the retriever find the right documents? Low score = retrieval failure.\n"
            "- **Context Precision (0–1):** Are retrieved docs all relevant, or is there noise? Low score = noisy retrieval.\n"
            "- **Implementation:** Each metric is a separate LLM call with a scoring rubric. No paid RAGAS library needed.",
        ),
        (
            "UC2 — LLM-as-Judge",
            "- **Problem:** Human evaluation is too slow and expensive at scale.\n"
            "- **Solution:** Use a second LLM to score responses on custom criteria. Works for any task — not just RAG.\n"
            "- **Criteria:** Accuracy (weight 2×), Relevance (2×), Clarity (1×), Completeness (1.5×), Conciseness (1×).\n"
            "- **Output:** Per-criterion scores (1–10), weighted average, winner A vs B, reasoning per criterion.\n"
            "- **Bias risks:** Position bias (always judge both orderings), verbosity bias (long ≠ better), self-preference (don't use same model as judge).",
        ),
        (
            "UC3 — Hallucination Detection",
            "- **Problem:** LLMs fabricate facts that sound plausible. RAGAS faithfulness is coarse — claim-level detection is finer.\n"
            "- **Step 1:** Extract 3–8 individual factual claims from the LLM response.\n"
            "- **Step 2:** Verify each claim against the source context — SUPPORTED, CONTRADICTED, or UNVERIFIABLE.\n"
            "- **Hallucination rate:** Fraction of claims not SUPPORTED. < 20 % = Low Risk, 20–50 % = Medium, > 50 % = High.\n"
            "- **Use when:** You need claim-level attribution, audit trails, or compliance evidence.",
        ),
        (
            "UC4 — Eval Pipeline",
            "- **Problem:** Testing individual responses is not enough — you need systematic quality measurement at scale.\n"
            "- **Solution:** Define a test dataset (question + expected answer + context). Run all metrics automatically.\n"
            "- **Dashboard:** Average scores per metric, per-case table with pass/fail, worst-performing cases highlighted.\n"
            "- **CI/CD integration:** Run the pipeline on every RAG config change to catch regressions before production.\n"
            "- **Good eval dataset:** Diverse questions, mix of difficulty, labelled ground truth, no test contamination.",
        ),
    ]
    for title, body in llmeval_details:
        with st.expander(title, expanded=False):
            st.markdown(body)

    st.divider()
    st.subheader("Fine-tuning — Coverage Map")
    st.write(
        "Four fine-tuning concepts from decision framework to production deployment — all without a GPU. "
        "Interactive calculators, LoRA math visualisations, and copy-ready code walkthroughs."
    )
    st.table({
        "UC": ["UC1", "UC2", "UC3", "UC4"],
        "Topic": [
            "Fine-tune vs RAG",
            "LoRA Architecture",
            "PEFT with HuggingFace",
            "Instruction Tuning",
        ],
        "What it demonstrates": [
            "Rule-based decision tree: when to fine-tune, when to use RAG, when to use both",
            "d×d → d×r + r×d parameter reduction (NumPy math + Plotly bar chart)",
            "LoraConfig → get_peft_model() → training loop → merge_and_unload() (copy-ready code)",
            "Alpaca / ChatML / ShareGPT format live preview + dataset quality checklist",
        ],
        "GPU required": ["No", "No", "No", "No"],
        "Status": [
            "✅ UC1 — live",
            "✅ UC2 — live",
            "✅ UC3 — live",
            "✅ UC4 — live",
        ],
    })

    st.markdown("##### What each UC teaches")
    finetune_details = [
        (
            "UC1 — Fine-tune vs RAG Decision Engine",
            "- **The core question:** Given my use case, should I fine-tune a model or use RAG?\n"
            "- **Fine-tune wins when:** Style transfer, classification, 500+ labeled examples, latency-critical (< 200 ms), knowledge is static.\n"
            "- **RAG wins when:** Factual Q&A over documents, knowledge changes frequently, fewer than 100 labeled examples, need source citations.\n"
            "- **Both wins when:** Need a specific brand voice (fine-tune) AND fresh knowledge (RAG) — e.g. customer support bots.\n"
            "- **Implementation:** Pure Python rule tree — instant results, no LLM call, no GPU.",
        ),
        (
            "UC2 — LoRA Architecture",
            "- **Problem:** Fine-tuning all 7B parameters requires 80+ GB GPU — impossible for most teams.\n"
            "- **Solution:** Only train two small matrices A (d×r, Gaussian init) and B (r×d, zero init) that approximate the weight update.\n"
            "- **Math:** ΔW = (α/r) × BA  — weight update is low-rank. At start B=0 so ΔW=0 (no disruption to base model).\n"
            "- **Parameter reduction:** For d=768, r=8 → original 590K → LoRA 12K → 48× fewer trainable params.\n"
            "- **Playground:** Sliders for d, r, alpha → live reduction stats + A/B matrix preview + bar chart.",
        ),
        (
            "UC3 — PEFT with HuggingFace",
            "- **PEFT (Parameter-Efficient Fine-Tuning):** Umbrella term covering LoRA, Prefix Tuning, Adapters, IA³.\n"
            "- **5-step pipeline:** `pip install peft` → `LoraConfig` → `get_peft_model()` → `TrainingArguments + Trainer` → `merge_and_unload()`.\n"
            "- **Playground:** Set base model, task type, r, alpha, target_modules → generates complete runnable code for all 5 steps.\n"
            "- **Memory estimate:** Shows GPU RAM required for different configs (8-bit quantisation + LoRA fits 7B in 8 GB GPU).\n"
            "- **merge_and_unload():** Folds LoRA adapters into base weights at inference time — no extra latency.",
        ),
        (
            "UC4 — Instruction Tuning",
            "- **What is instruction tuning?** Teaching a pre-trained base model to follow instructions (not just complete text).\n"
            "- **Alpaca format:** `### Instruction:` / `### Input:` / `### Response:` — simple, widely supported.\n"
            "- **ChatML format:** `<|im_start|>system/user/assistant<|im_end|>` — used by most modern chat models.\n"
            "- **ShareGPT format:** `{\"from\": \"human/gpt\", \"value\": ...}` — multi-turn conversation datasets.\n"
            "- **Playground:** Enter instruction/input/output → see live formatted preview in all 3 formats + download as JSON.\n"
            "- **Data quality rule:** 1,000 high-quality examples outperform 100,000 noisy ones.",
        ),
    ]
    for title, body in finetune_details:
        with st.expander(title, expanded=False):
            st.markdown(body)

    st.divider()
    st.subheader("System Design at Scale — Coverage Map")
    st.write(
        "Four interactive calculators answering the most common LLM system design interview questions. "
        "All pure Python — no API calls, fully interactive with live plotly charts."
    )
    st.table({
        "UC": ["UC1", "UC2", "UC3", "UC4"],
        "Calculator": [
            "Latency Budget",
            "Throughput & Scaling",
            "Architecture Patterns",
            "Cost Estimation",
        ],
        "What it computes": [
            "9-stage request waterfall (ms per stage, bottleneck, streaming vs non-streaming)",
            "RPS under 4 strategies: baseline, +cache, +batching, +both vs replica count",
            "Architecture recommendation (Single / Load-Balanced / Async Queue / Global CDN) from requirements",
            "Monthly cost (LLM tokens + embedding + infra) + cache ROI + cost-per-request",
        ],
        "Interview question it answers": [
            '"Where does latency go in a RAG system? How does streaming help?"',
            '"How do you scale from 5 RPS to 100 RPS?"',
            '"Walk me through the architecture for a production RAG system."',
            '"Estimate the monthly cost of serving 10K LLM requests/day."',
        ],
        "Status": [
            "✅ UC1 — live",
            "✅ UC2 — live",
            "✅ UC3 — live",
            "✅ UC4 — live",
        ],
    })

    st.markdown("##### Key numbers every AI Architect should know")
    st.code(
        "Typical RAG request latency breakdown:\n"
        "  Network (in)     ~20 ms\n"
        "  Embedding         ~15 ms   (all-MiniLM-L6-v2 on CPU)\n"
        "  Vector search     ~30 ms   (ChromaDB in-memory)\n"
        "  LLM TTFT         ~300 ms   (Groq, ~1000 token prompt)\n"
        "  LLM generation  ~1200 ms   (Groq, ~500 token response)\n"
        "  Post-process      ~10 ms\n"
        "  ─────────────────────────\n"
        "  Total (blocking) ~1600 ms   LLM = 94 % of total\n"
        "  Total (streaming)  ~345 ms  perceived (user sees first token)\n\n"
        "Scaling levers (at 1 replica, 1600 ms latency, no optimisation = 0.6 RPS):\n"
        "  +3 replicas                → 1.9 RPS  (3×)\n"
        "  +30 % cache hit rate       → 2.2 RPS  (3.6×)\n"
        "  +batch_size=4              → 2.4 RPS  (4×)\n"
        "  3 replicas + cache + batch → 8.5 RPS  (14×)\n\n"
        "Cost reference (10K requests/month, 1K input + 500 output tokens):\n"
        "  Groq free tier (openai/gpt-oss-20b)  →  $0/month\n"
        "  GPT-4o mini                          →  ~$2/month\n"
        "  GPT-4o                               →  ~$37/month",
        language="text",
    )


# ─── Tab 4 — Integrations ─────────────────────────────────────────────────────

def _integrations() -> None:
    st.subheader("Integration Map")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Groq API")
        st.write(
            "Used by T4 (RAG), T5 (Agent), T6 (Multi-Agent) for LLM inference. "
            "Model: `meta-llama/llama-4-scout-17b-16e-instruct` — fast, free tier."
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
            "data/loan_docs/loan_eligibility_sample.csv",
            "data/hr_docs/hr_attrition_sample.csv",
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
            "data/loan_docs/loan_policy.pdf",
            "data/hr_docs/hr_policy.txt",
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


# ─── Tab 7 — Glossary ────────────────────────────────────────────────────────

def _glossary() -> None:
    st.subheader("📚 Glossary — Plain English Definitions")
    st.write(
        "New to AI? These are the key terms you'll encounter across all apps on this platform. "
        "No jargon — just simple explanations."
    )

    terms = [
        ("Agent", "AI",
         "An AI that can take actions, not just generate text. "
         "An agent decides what to do (reason), does it (act), reads the result (observe), "
         "and repeats until the task is complete. It's like a worker, not just a calculator."),
        ("Chunk", "RAG",
         "A small piece of a larger document — usually a paragraph or a few sentences. "
         "Documents are split into chunks so the AI can search them efficiently. "
         "Smaller pieces are easier to match to a specific question."),
        ("Context Window", "LLM",
         "The maximum amount of text an AI model can read and remember in one call. "
         "Everything you send (instructions, history, documents) must fit inside this limit. "
         "Going over it means the AI forgets the oldest parts."),
        ("Embedding", "RAG / AI Opt",
         "A list of numbers that represents the *meaning* of a piece of text. "
         "Think of it as a fingerprint for language. "
         "Two sentences that mean the same thing have similar embeddings, "
         "even if the words are completely different."),
        ("Fallback", "AI Opt",
         "An automatic backup plan when the primary AI model fails or is too slow. "
         "Your app switches to a secondary model without the user noticing any interruption."),
        ("Fan-out / Fan-in", "MAS",
         "Fan-out: sending the same task to multiple agents at once. "
         "Fan-in: collecting all their outputs and combining them into one answer. "
         "Like distributing work to a team, then consolidating their reports."),
        ("Groundedness", "RAG",
         "An answer is 'grounded' if every claim it makes is supported by the documents provided. "
         "A grounded answer never makes things up — it only says what the sources support."),
        ("Hallucination", "LLM",
         "When an AI makes up facts that sound plausible but are wrong. "
         "Example: 'Einstein won the Nobel Prize in 1923' (it was 1921). "
         "RAG and grounding techniques help reduce hallucinations."),
        ("LLM", "Core",
         "Large Language Model — an AI trained on vast amounts of text that can read, write, "
         "reason, summarise, translate, and answer questions in natural language. "
         "Examples: GPT-4, LLaMA, Gemini."),
        ("MAS", "MAS",
         "Multi-Agent System — a system where multiple AI agents work together, "
         "each with a specific role, to complete a task that would be too complex for one agent alone."),
        ("RAG", "RAG",
         "Retrieval-Augmented Generation. A technique where the AI retrieves relevant information "
         "from your documents before generating a response. "
         "This gives the AI access to your specific knowledge without retraining it."),
        ("ReAct", "Agent",
         "Reason + Act — a pattern where an agent alternates between thinking about what to do "
         "and doing it (calling a tool), until it has enough information to answer. "
         "Every step is visible in the reasoning trace."),
        ("Semantic", "RAG / AI Opt",
         "Related to *meaning*, not exact words. "
         "'Semantic search' finds text that means the same thing as your query — "
         "even if it uses completely different words."),
        ("Similarity Score", "RAG / AI Opt",
         "A number between 0 and 1 measuring how similar two pieces of text are in meaning. "
         "1.0 = identical meaning. 0.85+ = essentially the same question. "
         "0.5 = related but different topics."),
        ("Streaming", "AI Opt",
         "Showing the AI's response word-by-word as it's generated, instead of waiting for the full response. "
         "It feels much faster because you start reading immediately — "
         "even though the total generation time is the same."),
        ("Token", "LLM",
         "The basic unit an AI processes — roughly a word or part of a word. "
         "'Hello world' is about 2 tokens. AI APIs charge by the number of tokens processed. "
         "The context window is measured in tokens."),
        ("Tool", "Agent",
         "A function that an AI agent can call to interact with the world: "
         "search Wikipedia, run a calculation, call an API, read a file. "
         "Tools give agents real-world capabilities that a plain LLM doesn't have."),
        ("Vector Store", "RAG",
         "A special database that stores embeddings (text fingerprints) and can search them "
         "very quickly by similarity. It's the 'smart filing cabinet' that makes RAG work. "
         "Examples used here: ChromaDB."),
        ("Whisper", "Media",
         "An AI model that converts spoken audio into text (speech-to-text). "
         "It handles multiple languages, accents, and background noise. "
         "Created by OpenAI, used here via Groq's fast inference."),
        ("RAGAS", "LLM Eval",
         "A framework for evaluating RAG systems. Four metrics: Faithfulness (is the answer grounded?), "
         "Answer Relevance (does it address the question?), Context Recall (right docs retrieved?), "
         "Context Precision (no noisy docs?). Each metric scores 0–1."),
        ("Faithfulness", "LLM Eval",
         "An evaluation metric measuring whether every claim in an LLM response is supported by "
         "the retrieved context. Score 1.0 = fully grounded, 0.0 = completely unsupported. "
         "Low faithfulness = high hallucination risk."),
        ("LLM-as-Judge", "LLM Eval",
         "Using a second LLM to evaluate the output of a first LLM on custom criteria like accuracy, "
         "clarity, and completeness. Scales human evaluation to millions of responses. "
         "Key risk: the judge model can have biases (position, verbosity, self-preference)."),
        ("Fine-tuning", "Fine-tuning",
         "Continuing the training of a pre-trained LLM on a specific dataset to specialise it for "
         "a particular task or domain. Cheaper than training from scratch. "
         "Fine-tuning vs RAG: fine-tune for style/format tasks, RAG for knowledge tasks."),
        ("LoRA", "Fine-tuning",
         "Low-Rank Adaptation — a parameter-efficient fine-tuning method that adds two small matrices "
         "A (d×r) and B (r×d) to each weight matrix instead of updating all parameters. "
         "For a 7B model with rank r=8, only 0.06 % of parameters are trained."),
        ("PEFT", "Fine-tuning",
         "Parameter-Efficient Fine-Tuning — umbrella term for methods that fine-tune only a small "
         "fraction of model parameters. LoRA is the most popular PEFT method. "
         "HuggingFace's `peft` library provides a unified API for all PEFT methods."),
        ("Instruction Tuning", "Fine-tuning",
         "A type of fine-tuning that teaches a base language model to follow instructions. "
         "Uses datasets formatted as (instruction, input, output) triples. "
         "Common formats: Alpaca, ChatML, ShareGPT."),
        ("Latency Budget", "System Design",
         "The total time allocated for one request to be processed end-to-end. "
         "Breaking it into stages (embedding, vector search, LLM TTFT, generation) shows "
         "where to focus optimisation. In RAG systems, LLM generation is typically 75 % of the budget."),
        ("TTFT", "System Design",
         "Time To First Token — how long the user waits before seeing the first word of the LLM response. "
         "With streaming enabled, perceived latency equals TTFT (~300 ms), not total generation time (~1600 ms). "
         "The most important UX latency metric for LLM applications."),
        ("Throughput", "System Design",
         "The number of requests a system can handle per second (RPS). "
         "Increased by adding replicas (horizontal scaling), semantic caching (reduce LLM calls), "
         "or request batching (share one LLM call across multiple requests)."),
    ]

    # Group by area
    col_left, col_right = st.columns(2)
    for i, (term, area, definition) in enumerate(sorted(terms, key=lambda x: x[0])):
        target = col_left if i % 2 == 0 else col_right
        with target:
            with st.container(border=True):
                st.markdown(f"**{term}** &nbsp; `{area}`")
                st.write(definition)
