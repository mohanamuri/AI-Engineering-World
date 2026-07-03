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
            },
            {
                "id": "loan_rag",
                "capability": "RAG",
                "tier": 4,
                "icon": "RAG",
                "status": "coming_soon",
                "difficulty": "Advanced",
                "version": "0.1.0",
                "stack": ["LangChain", "ChromaDB", "Sentence Transformers", "OpenAI"],
                "description": (
                    "Retrieval-Augmented Generation: ground loan decisions in "
                    "policy documents using a vector store and LLM reasoning."
                ),
            },
            {
                "id": "loan_agent",
                "capability": "AI Agent",
                "tier": 5,
                "icon": "AGT",
                "status": "coming_soon",
                "difficulty": "Advanced",
                "version": "0.1.0",
                "stack": ["LangGraph", "OpenAI", "pandas"],
                "description": (
                    "A single autonomous agent that runs the full eligibility "
                    "workflow: data validation, risk scoring, and decision rationale."
                ),
            },
            {
                "id": "loan_multi_agent",
                "capability": "Multi-Agent System",
                "tier": 6,
                "icon": "MAS",
                "status": "coming_soon",
                "difficulty": "Expert",
                "version": "0.1.0",
                "stack": ["CrewAI", "LangGraph", "OpenAI", "FastAPI"],
                "description": (
                    "Specialist agents (underwriter, fraud detector, compliance) "
                    "collaborate through a shared message bus to reach a consensus decision."
                ),
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
