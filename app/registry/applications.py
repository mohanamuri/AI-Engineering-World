"""
AI Engineering World — Application Registry

Structure: PROJECTS → apps (capability tiers)

One project = one real-world problem domain.
One app     = one capability tier within that project.

This design tells a clear story: the same problem solved progressively
with increasingly powerful AI techniques. Adding a new project requires
one new PROJECTS entry. Adding a new capability tier requires one new
entry inside the relevant project's "apps" list.

APPLICATIONS is derived from PROJECTS for backward compatibility with
the router and launcher (which map app IDs to runner functions).
"""

PROJECTS = [

    {
        "id": "loan_eligibility",
        "name": "Loan Eligibility Prediction",
        "short_name": "Loan Eligibility",
        "section": "Domain Projects",
        "icon": "💳",
        "category": "Finance · Credit Risk",
        "description": (
            "One financial problem solved progressively — from classical ML "
            "to multi-agent AI. Each tier unlocks a new capability on top of "
            "the same domain and dataset."
        ),
        "apps": [
            {
                "id": "loan_ml",

                "capability": "Machine Learning",
                "tier": 1,
                "icon": "ML",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["scikit-learn", "pandas", "plotly", "joblib"],
                "description": (
                    "Full ML pipeline: upload data, explore, preprocess, "
                    "train (LR / DT / RF / XGBoost), evaluate, and export artifacts."
                ),
                "what": "Uploaded a loan dataset, cleaned it, and trained 4 classical models to predict approval. Measured accuracy, precision, recall, and ROC AUC.",
                "why_next": "Classical models learn fixed rules. A neural network can discover complex, non-linear patterns automatically — potentially catching what rules miss.",
            },
            {
                "id": "loan_dl",
                "capability": "Deep Learning",
                "tier": 2,
                "icon": "DL",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["scikit-learn", "MLPClassifier", "pandas", "plotly"],
                "description": (
                    "Neural network approach using MLP. Compare loss curves, "
                    "architecture diagrams, and accuracy against the ML baseline."
                ),
                "what": "Replaced classical models with a Multi-Layer Perceptron. Trained over multiple epochs, watched the loss curve drop, and compared accuracy against the T1 baseline.",
                "why_next": "The neural network predicts well but can't explain why. In finance, regulators and customers demand a clear reason for every approval or rejection.",
            },
            {
                "id": "loan_xai",
                "capability": "Explainability",
                "tier": 3,
                "icon": "XAI",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["SHAP", "LIME", "scikit-learn", "plotly"],
                "description": (
                    "Explain black-box model decisions using SHAP values and "
                    "LIME. Understand feature contributions per prediction."
                ),
                "what": "Used SHAP to show which features drove each prediction globally and locally. Used LIME as an independent cross-check with a simple linear approximation.",
                "why_next": "Explanations are still static — a loan officer can't ask follow-up questions. What if they could query the model and policy documents in plain English?",
            },
            {
                "id": "loan_rag",
                "capability": "RAG",
                "tier": 4,
                "icon": "RAG",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangChain", "ChromaDB", "Groq", "HuggingFace"],
                "description": (
                    "Retrieval-Augmented Generation: ground loan decisions in "
                    "policy documents using a vector store and LLM reasoning."
                ),
                "what": "Store loan policy documents in a vector database. An LLM retrieves the relevant policy chunks and answers questions — grounded in facts, not hallucination.",
                "why_next": "RAG answers questions but still waits for a human to ask them. An autonomous agent can read an application, run checks, and produce a decision on its own.",
            },
            {
                "id": "loan_agent",
                "capability": "AI Agent",
                "tier": 5,
                "icon": "AGT",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "pandas"],
                "description": (
                    "A single autonomous agent that runs the full eligibility "
                    "workflow: data validation, risk scoring, and decision rationale."
                ),
                "what": "A single LLM-powered agent uses tools (validator, risk scorer, policy lookup) to autonomously process a loan application and write a structured decision report.",
                "why_next": "One agent handles everything sequentially. Real loan decisions involve multiple specialists — splitting into expert agents makes the system faster and more auditable.",
            },
            {
                "id": "loan_multi_agent",
                "capability": "Multi-Agent System",
                "tier": 6,
                "icon": "MAS",
                "status": "live",
                "difficulty": "Expert",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "FastAPI"],
                "description": (
                    "Specialist agents (underwriter, fraud detector, compliance) "
                    "collaborate through a shared message bus to reach a consensus decision."
                ),
                "what": "Three specialist agents — Underwriter, Fraud Detector, Compliance Officer — each analyse the application independently. A Supervisor synthesises a final consensus decision.",
                "why_next": "This is the final tier. It mirrors how real loan decisions work in banks — multiple expert teams, each contributing, reaching a governed consensus.",
            },
        ],
    },

    {
        "id": "hr_analytics",
        "name": "HR Analytics — Employee Attrition",
        "short_name": "HR Analytics",
        "section": "Domain Projects",
        "icon": "👥",
        "category": "Human Resources · Talent Retention",
        "description": (
            "One HR problem solved progressively — predict, explain, and prevent "
            "employee attrition. Each tier unlocks a new capability on the same "
            "domain, from classical ML to a multi-agent expert panel."
        ),
        "apps": [
            {
                "id": "hr_ml",
                "capability": "Machine Learning",
                "tier": 1,
                "icon": "ML",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["scikit-learn", "pandas", "plotly", "joblib"],
                "description": (
                    "Full ML pipeline: upload HR data, explore attrition signals, "
                    "preprocess features, train 4 classifiers (LR / DT / RF / XGBoost), "
                    "evaluate with F1 and ROC AUC, and export artifacts."
                ),
                "what": "Uploaded an HR attrition dataset, engineered features, trained four classifiers with balanced class weights to handle the attrition imbalance, and evaluated with F1 and ROC AUC.",
                "why_next": "Classical models predict attrition but cannot explain why an employee is at risk. Neural networks can discover more complex patterns automatically.",
            },
            {
                "id": "hr_dl",
                "capability": "Deep Learning",
                "tier": 2,
                "icon": "DL",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["scikit-learn", "MLPClassifier", "pandas", "plotly"],
                "description": (
                    "Neural network approach using MLP with balanced sample weights. "
                    "Watch the loss curve converge and compare against the classical baseline."
                ),
                "what": "Replaced classical models with a Multi-Layer Perceptron. Applied balanced sample weights to handle class imbalance. Tracked training loss per epoch.",
                "why_next": "The neural network predicts well but is a black box. HR managers need to know *why* an employee is flagged — which factors are actually driving the risk.",
            },
            {
                "id": "hr_xai",
                "capability": "Explainability",
                "tier": 3,
                "icon": "XAI",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["SHAP", "LIME", "scikit-learn", "plotly"],
                "description": (
                    "Explain every attrition prediction globally and locally using "
                    "SHAP and LIME. See exactly which factors drive each employee's risk."
                ),
                "what": "Used SHAP to identify which HR factors most drive attrition globally. Used LIME to explain individual flight-risk predictions for specific employees.",
                "why_next": "Explanations are static — an HR manager can't ask follow-up questions about retention policy. What if they could query policy documents in plain English?",
            },
            {
                "id": "hr_rag",
                "capability": "RAG",
                "tier": 4,
                "icon": "RAG",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangChain", "ChromaDB", "Groq", "HuggingFace"],
                "description": (
                    "Upload any HR policy document and ask natural-language questions. "
                    "Every answer is grounded in the document — no hallucination."
                ),
                "what": "Embedded HR policy documents into ChromaDB. An LLM retrieves relevant policy chunks and answers HR questions — grounded in facts, not hallucination.",
                "why_next": "RAG answers questions but still waits for a human to ask. An autonomous agent can take an employee profile, run all checks, and produce a risk report on its own.",
            },
            {
                "id": "hr_agent",
                "capability": "AI Agent",
                "tier": 5,
                "icon": "AGT",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "LangChain Tools"],
                "description": (
                    "A single autonomous agent validates employee data, computes an "
                    "attrition risk score, looks up retention policy, and writes "
                    "a structured risk report with actionable interventions."
                ),
                "what": "A single LLM-powered agent ran three tools (validator, risk scorer, policy lookup) and synthesised a structured attrition risk report with recommended interventions.",
                "why_next": "One agent handles everything sequentially. Real HR risk assessments involve multiple specialists — splitting into expert agents makes the system more robust and auditable.",
            },
            {
                "id": "hr_multi_agent",
                "capability": "Multi-Agent System",
                "tier": 6,
                "icon": "MAS",
                "status": "live",
                "difficulty": "Expert",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Multi-Agent"],
                "description": (
                    "Three specialist agents — HR Manager, Performance Evaluator, and "
                    "Risk Assessor — each independently analyse the employee. "
                    "The HR Director synthesises a consensus attrition risk decision."
                ),
                "what": "Three independent LLM specialists each analysed the employee from their domain perspective. The HR Director resolved any disagreements and synthesised a final consensus decision.",
                "why_next": "This is the final tier. It mirrors how real HR decisions work — multiple expert teams contributing, an HR Director governing the final call.",
            },
        ],
    },

    {
        "id": "rag_projects",
        "name": "RAG Projects",
        "short_name": "RAG Projects",
        "section": "RAG Projects",
        "icon": "📚",
        "category": "Retrieval · LLM · Vector Search",
        "description": (
            "Retrieval-Augmented Generation — seven progressively advanced use cases. "
            "From querying multiple documents to knowledge graphs, corrective retrieval, "
            "and modular pipelines — each use case adds one new RAG capability."
        ),
        "apps": [
            {
                "id": "rag_uc1",
                "capability": "Multi-Document RAG",
                "tier": 1,
                "tier_label": "UC",
                "icon": "RAG",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["LangChain", "ChromaDB", "Groq", "HuggingFace"],
                "description": (
                    "Upload multiple documents simultaneously. All chunks are embedded "
                    "into a single vector store with source metadata — every answer "
                    "shows exactly which document it came from."
                ),
                "what": "Uploaded 3 documents into a shared vector store. Each chunk retains its source filename. Asked cross-document questions and saw exactly which document contributed each part of the answer.",
                "why_next": "Multi-doc RAG uses dense vector similarity alone. Adding keyword-based (BM25) retrieval alongside vector search finds answers that embeddings alone might miss — especially for exact terms and technical jargon.",
            },
            {
                "id": "rag_uc2",
                "capability": "Hybrid Search RAG",
                "tier": 2,
                "tier_label": "UC",
                "icon": "RAG",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangChain", "BM25", "ChromaDB", "Groq"],
                "description": (
                    "Combine dense vector search with sparse BM25 keyword retrieval. "
                    "Reciprocal rank fusion merges both result sets for higher recall "
                    "on exact terms and technical jargon."
                ),
                "what": "Combined cosine-similarity vector search with BM25 keyword matching. RRF fusion improved recall for exact product names and technical terms that embeddings struggled with.",
                "why_next": "Hybrid search improves retrieval but the pipeline is still passive — it retrieves once per query. An agent can decide when to search, how many times, and whether the retrieved context is sufficient.",
            },
            {
                "id": "rag_uc3",
                "capability": "Agentic RAG",
                "tier": 3,
                "tier_label": "UC",
                "icon": "RAG",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangGraph", "LangChain", "Groq", "ChromaDB"],
                "description": (
                    "An LLM agent decides whether to retrieve, reformulates queries "
                    "when context is insufficient, and iterates until it has enough "
                    "information to answer confidently."
                ),
                "what": "The agent first classified whether retrieval was needed, then retrieved, evaluated context quality, reformulated the query if needed, and only generated an answer when confident.",
                "why_next": "Agentic RAG retrieves adaptively but still generates answers without self-evaluation. Self-RAG adds an explicit critic step: the model checks its own output and rewrites if it fails quality criteria.",
            },
            {
                "id": "rag_uc4",
                "capability": "Self-RAG",
                "tier": 4,
                "tier_label": "UC",
                "icon": "RAG",
                "status": "live",
                "difficulty": "Expert",
                "version": "1.0.0",
                "stack": ["LangGraph", "LangChain", "Groq", "ChromaDB"],
                "description": (
                    "The model generates an answer, then evaluates it on three criteria: "
                    "grounded in context, relevant to the question, and complete. "
                    "Low scores trigger a rewrite loop."
                ),
                "what": "After generating each answer the model scored it on groundedness, relevance, and completeness. Scores below threshold triggered a query reformulation and re-retrieval cycle.",
                "why_next": "Self-RAG evaluates generation quality but retrieval is still similarity-based. GraphRAG changes the retrieval method entirely — using a knowledge graph to follow entity relationships.",
            },
            {
                "id": "rag_uc5",
                "capability": "GraphRAG",
                "tier": 5,
                "tier_label": "UC",
                "icon": "RAG",
                "status": "live",
                "difficulty": "Expert",
                "version": "1.0.0",
                "stack": ["LangChain", "ChromaDB", "Groq", "Knowledge Graph", "BFS"],
                "description": (
                    "LLM extracts entities and relationships from your documents to build "
                    "a Knowledge Graph. Answers are found by traversing the graph — "
                    "discovering connected information that simple similarity search misses."
                ),
                "what": "LLM extracted entity-relation triples from each chunk to build a knowledge graph. Queries were resolved by matching entities then expanding via BFS traversal — finding indirectly related chunks.",
                "why_next": "GraphRAG changes how retrieval works. Corrective RAG (CRAG) adds a different innovation — validating whether retrieved chunks are actually relevant before generating, with external fallback.",
            },
            {
                "id": "rag_uc6",
                "capability": "Corrective RAG (CRAG)",
                "tier": 6,
                "tier_label": "UC",
                "icon": "RAG",
                "status": "live",
                "difficulty": "Expert",
                "version": "1.0.0",
                "stack": ["LangChain", "ChromaDB", "Groq", "Wikipedia API", "Relevance Grading"],
                "description": (
                    "Every retrieved chunk is graded CORRECT, AMBIGUOUS, or INCORRECT. "
                    "If local documents are insufficient, CRAG automatically fetches "
                    "supplementary information from Wikipedia — no API key required."
                ),
                "what": "LLM graded each retrieved chunk as CORRECT/AMBIGUOUS/INCORRECT. Based on grades, the system decided to use local docs only, Wikipedia only, or both — making RAG reliable even when docs don't cover the question.",
                "why_next": "CRAG adds correction to retrieval. Modular RAG goes further — making the entire pipeline configurable so you can combine Dense, Sparse, and Reranker modules in any combination.",
            },
            {
                "id": "rag_uc7",
                "capability": "Modular RAG",
                "tier": 7,
                "tier_label": "UC",
                "icon": "RAG",
                "status": "live",
                "difficulty": "Expert",
                "version": "1.0.0",
                "stack": ["LangChain", "ChromaDB", "BM25", "Groq Reranker", "RRF Fusion"],
                "description": (
                    "Three independent retrieval modules — Dense (ChromaDB), Sparse (BM25), "
                    "and Reranker (LLM) — that you can toggle on/off. Results are fused "
                    "with Reciprocal Rank Fusion. See exactly what each module contributes."
                ),
                "what": "Toggled Dense, Sparse (BM25), and LLM Reranker modules independently. RRF fusion merged their ranked lists. Each chunk in the answer shows which modules contributed to its ranking.",
                "why_next": "This is the final tier. Modular RAG completes the progression: retrieval (UC1) → hybrid (UC2) → agentic (UC3) → self-evaluated (UC4) → graph-based (UC5) → corrective (UC6) → fully modular (UC7).",
            },
        ],
    },

    {
        "id": "agent_projects",
        "name": "Agent Projects",
        "short_name": "Agent Projects",
        "section": "Agent Projects",
        "icon": "🤖",
        "category": "Autonomous Agents · LangGraph · Tools",
        "description": (
            "Standalone LangGraph agent showcases — four progressively advanced architectures. "
            "From a simple tool-use loop to a multi-agent supervisor system, "
            "each use case adds one new architectural concept."
        ),
        "apps": [
            {
                "id": "agent_uc1",
                "capability": "ReAct Agent",
                "tier": 1,
                "tier_label": "UC",
                "icon": "AGT",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Wikipedia API", "Calculator"],
                "description": (
                    "The classic Reason+Act loop: the LLM reasons about what to do, "
                    "calls a tool, observes the result, and reasons again — cycling "
                    "until it can answer. Every step is visible."
                ),
                "what": "The agent reasoned step-by-step and called tools (Wikipedia, Calculator) as needed. Each thought, tool call, and observation was captured in a trace.",
                "why_next": "ReAct reacts one step at a time with no upfront plan. Plan-and-Execute separates planning from execution — the agent creates a full plan before taking any action.",
            },
            {
                "id": "agent_uc2",
                "capability": "Plan-and-Execute Agent",
                "tier": 2,
                "tier_label": "UC",
                "icon": "AGT",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Wikipedia API", "Calculator"],
                "description": (
                    "Before acting, the agent creates a numbered multi-step plan. "
                    "An executor runs each step in order (calling tools where needed), "
                    "then a responder synthesises all results."
                ),
                "what": "The planner created a multi-step plan upfront. The executor ran each step using appropriate tools. The responder synthesised all step results into a coherent final answer.",
                "why_next": "Plan-and-Execute runs a static plan. A Reflection agent can evaluate its own output quality and rewrite if needed — without any external tools.",
            },
            {
                "id": "agent_uc3",
                "capability": "Reflection Agent",
                "tier": 3,
                "tier_label": "UC",
                "icon": "AGT",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Self-Critique Loop"],
                "description": (
                    "The agent writes a draft, then acts as its own critic — scoring "
                    "Clarity, Accuracy, and Completeness (1–5 each). Low scores trigger "
                    "a targeted rewrite. No external tools required."
                ),
                "what": "After each draft the agent scored its own output on three dimensions. Scores below the threshold triggered a targeted rewrite, with the critique embedded in the next prompt.",
                "why_next": "Reflection is a single agent talking to itself. Multi-Agent systems split cognition across specialists — each agent only does one thing, coordinated by a Supervisor.",
            },
            {
                "id": "agent_uc4",
                "capability": "Multi-Agent Supervisor",
                "tier": 4,
                "tier_label": "UC",
                "icon": "AGT",
                "status": "live",
                "difficulty": "Expert",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Supervisor Pattern", "Wikipedia API", "Calculator"],
                "description": (
                    "A Supervisor LLM routes tasks to three specialists: "
                    "a Researcher (Wikipedia), an Analyst (Calculator), and a Writer. "
                    "After each specialist acts, the Supervisor re-evaluates until done."
                ),
                "what": "The Supervisor routed sub-tasks to Researcher, Analyst, and Writer agents. Each specialist contributed its domain output. The Writer synthesised a final answer from all contributions.",
                "why_next": "This is the final tier. It mirrors how real teams work: a manager coordinates specialists rather than doing everything alone.",
            },
        ],
    },

    {
        "id": "mas_projects",
        "name": "MAS Projects",
        "short_name": "Multi-Agent Projects",
        "section": "Multi-Agent Projects",
        "icon": "🕸️",
        "category": "Multi-Agent Systems · LangGraph · Coordination",
        "description": (
            "Standalone LangGraph multi-agent showcases — four progressively advanced architectures. "
            "From a fixed sequential pipeline to an adversarial debate to a full research crew, "
            "each use case introduces a distinct MAS coordination pattern."
        ),
        "apps": [
            {
                "id": "mas_uc1",
                "capability": "Supervisor Pipeline",
                "tier": 1,
                "tier_label": "UC",
                "icon": "MAS",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Pipeline Pattern", "Wikipedia API"],
                "description": (
                    "A fixed sequential pipeline: Collector gathers facts, Processor extracts insights, "
                    "Writer drafts the response, Supervisor closes with an executive summary. "
                    "Each agent receives the previous agent's output as its primary input."
                ),
                "what": "The Supervisor coordinated a fixed 4-stage pipeline. Each agent received the previous stage's output, accumulating knowledge from Collector → Processor → Writer → Supervisor.",
                "why_next": "A pipeline is sequential and deterministic. Parallel Agents removes the dependency chain — three independent specialists tackle the same task simultaneously, then merge.",
            },
            {
                "id": "mas_uc2",
                "capability": "Parallel Agents",
                "tier": 2,
                "tier_label": "UC",
                "icon": "MAS",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Fan-out / Fan-in", "Wikipedia API"],
                "description": (
                    "Three independent specialist agents tackle the same task from different angles "
                    "(Facts, Critic, Creative) with no shared intermediate state. "
                    "An Aggregator merges all three perspectives into one coherent answer."
                ),
                "what": "Three independent agents produced separate perspectives without sharing context. The Aggregator synthesised a richer, more balanced answer than any single agent could.",
                "why_next": "Parallel agents cooperate. An adversarial pattern goes further — two agents actively oppose each other, surfacing trade-offs a cooperative team might miss.",
            },
            {
                "id": "mas_uc3",
                "capability": "Debate & Judge",
                "tier": 3,
                "tier_label": "UC",
                "icon": "MAS",
                "status": "live",
                "difficulty": "Advanced",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Adversarial Pattern", "Conditional Routing"],
                "description": (
                    "Two adversarial agents argue opposing positions across multiple rounds. "
                    "A neutral Judge evaluates both sides on logic, evidence, and persuasion, "
                    "then declares a winner. "
                    "A conditional edge controls how many rounds run."
                ),
                "what": "Proponent and Opponent argued back and forth for N rounds. The Judge evaluated the full debate and declared a winner based on logic, evidence, and persuasion quality.",
                "why_next": "Debate is adversarial but still a flat two-agent pattern. A Research Team is hierarchical with multiple specialised roles, memory, and an iterative research loop.",
            },
            {
                "id": "mas_uc4",
                "capability": "Research Team",
                "tier": 4,
                "tier_label": "UC",
                "icon": "MAS",
                "status": "live",
                "difficulty": "Expert",
                "version": "1.0.0",
                "stack": ["LangGraph", "Groq", "Iterative Research Loop", "Wikipedia API"],
                "description": (
                    "A full four-agent research crew: Planner breaks the query into questions, "
                    "Researcher answers each one (Wikipedia, called in a loop), "
                    "Analyst synthesises all findings, Writer produces the final report. "
                    "Memory accumulates across every stage."
                ),
                "what": "The Planner decomposed the query into sub-questions. The Researcher looped once per question. The Analyst synthesised all findings. The Writer produced a comprehensive report.",
                "why_next": "This is the final tier. It demonstrates the most complete MAS pattern: multi-role pipeline, iterative sub-task execution, and memory passing across all stages.",
            },
        ],
    },


    {
        "id": "prompt_projects",
        "name": "Prompt Engineering",
        "short_name": "Prompt Engineering",
        "section": "Prompt Engineering",
        "icon": "✍️",
        "category": "Prompt Design · LLM · Groq",
        "description": (
            "Four core prompting techniques — from zero-shot basics to multi-step chains. "
            "Each use case teaches one technique via concept, interactive playground, "
            "side-by-side comparison, and actionable insights."
        ),
        "apps": [
            {
                "id": "prompt_uc1",
                "capability": "Zero-shot vs Few-shot",
                "tier": 1,
                "tier_label": "UC",
                "icon": "✍️",
                "status": "live",
                "difficulty": "Beginner",
                "version": "1.0.0",
                "stack": ["Groq", "llama-3.1-8b-instant", "Streamlit"],
                "description": (
                    "Run the same task with zero examples vs 2–3 demonstrations. "
                    "See how few-shot examples anchor the model's output style and consistency, "
                    "and measure the token overhead of adding examples."
                ),
                "what": "Ran the same task zero-shot and few-shot. Compared output style, consistency, and token cost. Learned when examples help and when they're overkill.",
                "why_next": "Zero/few-shot controls what examples the model sees. Chain-of-Thought controls how it reasons — adding explicit step-by-step thinking before answering.",
            },
            {
                "id": "prompt_uc2",
                "capability": "Chain-of-Thought",
                "tier": 2,
                "tier_label": "UC",
                "icon": "✍️",
                "status": "live",
                "difficulty": "Beginner",
                "version": "1.0.0",
                "stack": ["Groq", "llama-3.1-8b-instant", "Streamlit"],
                "description": (
                    "Add 'Let's think step by step' to unlock the model's reasoning ability. "
                    "Compare direct answers vs step-by-step reasoning on math, logic, "
                    "and multi-step problems — no examples needed."
                ),
                "what": "Compared direct answers vs Chain-of-Thought reasoning on logic and math problems. Observed how visible reasoning steps reduce errors and improve accuracy.",
                "why_next": "CoT controls reasoning depth. Structured Output controls output shape — forcing JSON so downstream code can parse the result reliably every time.",
            },
            {
                "id": "prompt_uc3",
                "capability": "Structured Output",
                "tier": 3,
                "tier_label": "UC",
                "icon": "✍️",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq", "llama-3.1-8b-instant", "JSON Schema", "Streamlit"],
                "description": (
                    "Force the model to return valid JSON matching an exact schema every time. "
                    "Compare freeform prose vs structured JSON on the same extraction task — "
                    "and see which one your downstream code can actually use."
                ),
                "what": "Extracted information as freeform text vs structured JSON. Defined a schema, forced JSON output, parsed it with json.loads(). Learned schema design best practices.",
                "why_next": "Structured output controls one response's shape. Prompt Chaining controls the pipeline — breaking complex tasks into sequential steps for higher overall quality.",
            },
            {
                "id": "prompt_uc4",
                "capability": "Prompt Chaining",
                "tier": 4,
                "tier_label": "UC",
                "icon": "✍️",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq", "llama-3.1-8b-instant", "Streamlit"],
                "description": (
                    "Decompose complex tasks into a three-step chain: Outline → Draft → Refine. "
                    "Each step is focused and feeds the next. "
                    "Compare the chain output against a single monolithic prompt on the same task."
                ),
                "what": "Ran Outline → Draft → Refine as separate focused prompts. Compared the chain output against a single prompt. Observed quality gains and measured latency/token overhead.",
                "why_next": "This completes the Prompt Engineering arc: examples (UC1) → reasoning (UC2) → output shape (UC3) → pipeline (UC4). Together these four techniques cover production prompt engineering.",
            },
        ],
    },

    {
        "id": "aiopt_projects",
        "name": "AI Optimisation Techniques",
        "short_name": "AI Optimisation",
        "section": "AI Optimisation Techniques",
        "icon": "⚙️",
        "category": "LLM Optimisation · Cost · Performance · Resilience",
        "description": (
            "Four production LLM optimisation patterns — from semantic caching to model routing, "
            "memory management to streaming and fallback. "
            "Each use case teaches one technique via concept, interactive playground, "
            "side-by-side comparison, and actionable insights with interview Q&A."
        ),
        "apps": [
            {
                "id": "aiopt_uc1",
                "capability": "Semantic Caching",
                "tier": 1,
                "tier_label": "UC",
                "icon": "⚙️",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq", "sentence-transformers", "all-MiniLM-L6-v2", "NumPy", "Streamlit"],
                "description": (
                    "Skip redundant LLM calls using vector similarity. "
                    "Embed queries with sentence-transformers, find semantically similar cached responses "
                    "above a cosine-similarity threshold, and return them instantly — reducing cost and latency."
                ),
                "what": "Embedded user queries into 384-dim vectors. On each new query, searched the in-memory cache by cosine similarity. Cache hits returned instantly without an LLM call.",
                "why_next": "Caching avoids repeat calls. Model Routing goes further — for unavoidable calls, route each query to the cheapest model that can handle it well.",
            },
            {
                "id": "aiopt_uc2",
                "capability": "Model Routing",
                "tier": 2,
                "tier_label": "UC",
                "icon": "⚙️",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq", "llama-3.1-8b-instant", "llama-3.1-70b-versatile", "Streamlit"],
                "description": (
                    "A lightweight classifier reads each query and decides whether to use "
                    "the fast 8B model or the powerful 70B model. "
                    "Simple queries go to 8B; complex queries go to 70B. "
                    "Reduce API cost by 60–80 % without sacrificing quality."
                ),
                "what": "A complexity classifier (one 8B call, max 5 tokens) labelled each query SIMPLE or COMPLEX. Simple queries ran on the 8B model; complex ones escalated to the 70B model.",
                "why_next": "Routing controls which model runs. Memory Patterns control what context the model receives — essential for maintaining coherent multi-turn conversations.",
            },
            {
                "id": "aiopt_uc3",
                "capability": "Memory Patterns",
                "tier": 3,
                "tier_label": "UC",
                "icon": "⚙️",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq", "llama-3.1-8b-instant", "Buffer Memory", "Summary Memory", "Entity Memory"],
                "description": (
                    "Three memory strategies for multi-turn LLM conversations: "
                    "Buffer (keep last N messages), Summary (compress old turns with LLM), "
                    "and Entity (extract named entities into a persistent fact store). "
                    "No LangChain required — built from scratch with Groq."
                ),
                "what": "Implemented three memory strategies from scratch. Compared how each handles a 10-turn conversation — measuring tokens sent, context quality, and extra LLM calls required.",
                "why_next": "Memory controls what the model knows. Streaming + Fallback control how reliably and quickly the model delivers its response in production.",
            },
            {
                "id": "aiopt_uc4",
                "capability": "Streaming + Fallback",
                "tier": 4,
                "tier_label": "UC",
                "icon": "⚙️",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq", "Token Streaming", "SSE", "Retry + Backoff", "Model Fallback"],
                "description": (
                    "Two production resilience patterns: Streaming returns tokens as they generate — "
                    "perceived latency drops 70–90 %. Fallback retries the primary model then "
                    "automatically switches to a backup on failure. Essential for reliable LLM APIs."
                ),
                "what": "Implemented Groq streaming with st.write_stream() for real-time token delivery. Built retry-with-backoff fallback that switches to the 70B model when the primary fails.",
                "why_next": "This completes the AI Optimisation arc: cache (UC1) → route (UC2) → remember (UC3) → stream reliably (UC4). Together these four patterns underpin production LLM systems.",
            },
        ],
    },

    {
        "id": "media_projects",
        "name": "Media Intelligence",
        "short_name": "Media Projects",
        "section": "Media Projects",
        "icon": "🎬",
        "category": "Multimodal AI · Audio · Vision · Groq",
        "description": (
            "Four multimodal AI use cases — audio, video, image, and document — "
            "all powered by Groq free-tier APIs. "
            "From speech-to-text meeting reports to OCR-free document digitisation, "
            "each use case adds one new media modality."
        ),
        "apps": [
            {
                "id": "media_uc1",
                "capability": "Meeting Intelligence",
                "tier": 1,
                "tier_label": "UC",
                "icon": "🎙️",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq Whisper", "Groq LLM", "Streamlit"],
                "description": (
                    "Upload any audio recording (.mp3/.wav/.m4a). "
                    "Groq Whisper transcribes it, then an LLM extracts a structured report: "
                    "summary, decisions, action items, sentiment, and key topics."
                ),
                "what": "Uploaded a meeting audio file. Groq Whisper produced the transcript. An LLM extracted a structured JSON report with summary, decisions, action items, and sentiment.",
                "why_next": "Meeting Intelligence handles audio. Video Intelligence extends the same pipeline to video files by adding an ffmpeg audio-extraction step first.",
            },
            {
                "id": "media_uc2",
                "capability": "Video Intelligence",
                "tier": 2,
                "tier_label": "UC",
                "icon": "🎬",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["ffmpeg", "Groq Whisper", "Groq LLM", "Streamlit"],
                "description": (
                    "Upload a video file (.mp4/.mov). "
                    "ffmpeg extracts the audio track (16 kHz mono). "
                    "Groq Whisper transcribes it. "
                    "The same LLM extraction pipeline as UC1 produces the report."
                ),
                "what": "Uploaded a video file. ffmpeg stripped the audio track (16 kHz mono MP3). Groq Whisper transcribed it. The same UC1 LLM pipeline produced a structured meeting report.",
                "why_next": "Audio and video use speech-to-text. Image Intelligence shifts modality entirely — a vision LLM processes raw pixels with no audio or OCR pipeline.",
            },
            {
                "id": "media_uc3",
                "capability": "Image Intelligence",
                "tier": 3,
                "tier_label": "UC",
                "icon": "🖼️",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq Vision", "llama-4-scout-17b", "LangChain", "Streamlit"],
                "description": (
                    "Upload any image (.jpg/.png). "
                    "Groq Vision describes the scene, extracts all embedded text, "
                    "identifies objects and dominant colours, "
                    "then answers follow-up questions interactively."
                ),
                "what": "Uploaded an image. Groq Vision (llama-4-scout-17b) returned a structured JSON: scene description, extracted text, objects, colours. Then answered interactive follow-up questions.",
                "why_next": "Image Intelligence handles general photos. Document Scanner specialises on structured document digitisation — extracting title, sections, and metadata from document photos.",
            },
            {
                "id": "media_uc4",
                "capability": "Document Scanner",
                "tier": 4,
                "tier_label": "UC",
                "icon": "📄",
                "status": "live",
                "difficulty": "Intermediate",
                "version": "1.0.0",
                "stack": ["Groq Vision", "llama-4-scout-17b", "LangChain", "Streamlit"],
                "description": (
                    "Upload a photo of any document, whiteboard, or slide. "
                    "Groq Vision extracts structured content: document type, title, "
                    "sections with headings, all verbatim text, and metadata. "
                    "Export as JSON or plain text."
                ),
                "what": "Uploaded a document photo. Groq Vision returned structured JSON: document type, title, sections with headings, all verbatim text, and metadata (language, tables, diagrams).",
                "why_next": "This is the final tier of Media Projects: audio → video → image → structured document. Together they cover the four primary media modalities in enterprise AI workflows.",
            },
        ],
    },

]


# ---------------------------------------------------------------------------
# Flat APPLICATIONS list — derived automatically from PROJECTS.
# Used by the router, launcher, and any code expecting the old flat format.
# Do NOT edit this manually.
# ---------------------------------------------------------------------------

APPLICATIONS = [
    {
        "id": app["id"],
        "name": project["name"],
        "subtitle": app["capability"],
        "icon": app["icon"],
        "category": project["category"],
        "status": "Live" if app["status"] == "live" else "Coming Soon",
        "version": app["version"],
        "difficulty": app["difficulty"],
        "description": app["description"],
        "stack": app["stack"],
        # Project context (for display)
        "project_id": project["id"],
        "project_name": project["name"],
        "tier": app["tier"],
    }
    for project in PROJECTS
    for app in project["apps"]
]
