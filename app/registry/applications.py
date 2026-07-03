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
                "stack": ["LangChain", "ChromaDB", "Ollama", "nomic-embed-text"],
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
                "status": "coming_soon",
                "difficulty": "Advanced",
                "version": "0.1.0",
                "stack": ["LangGraph", "Ollama", "pandas"],
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
                "status": "coming_soon",
                "difficulty": "Expert",
                "version": "0.1.0",
                "stack": ["LangGraph", "Ollama", "FastAPI"],
                "description": (
                    "Specialist agents (underwriter, fraud detector, compliance) "
                    "collaborate through a shared message bus to reach a consensus decision."
                ),
                "what": "Three specialist agents — Underwriter, Fraud Detector, Compliance Officer — each analyse the application independently. A Supervisor synthesises a final consensus decision.",
                "why_next": "This is the final tier. It mirrors how real loan decisions work in banks — multiple expert teams, each contributing, reaching a governed consensus.",
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
