"""Fine-tune vs RAG decision framework — pure Python rule tree."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class FineTuneScenario:
    # Data availability
    labeled_examples: int            # number of task-specific examples available
    data_is_proprietary: bool        # is the training data confidential?
    # Task characteristics
    task_type: str                   # "style", "domain_knowledge", "instruction_following", "factual_qa", "classification"
    knowledge_changes_frequently: bool
    latency_critical: bool           # sub-200ms required
    # Constraints
    gpu_available: bool
    budget_monthly_usd: float
    need_explainability: bool


@dataclass
class FineTuneDecision:
    recommendation: str              # "Fine-tune", "RAG", "Both", "Neither — use base model"
    confidence: str                  # "High", "Medium", "Low"
    primary_reason: str
    pros: list[str]
    cons: list[str]
    when_to_reconsider: str


def should_finetune(scenario: FineTuneScenario) -> FineTuneDecision:
    """Rule-based decision tree for fine-tune vs RAG."""

    # Hard RAG signals
    if scenario.knowledge_changes_frequently:
        return FineTuneDecision(
            recommendation="RAG",
            confidence="High",
            primary_reason="Knowledge changes frequently — fine-tuning would require constant retraining",
            pros=["Always up-to-date", "No retraining cost", "Add/remove docs instantly"],
            cons=["Requires vector DB infrastructure", "Retrieval can fail for complex queries"],
            when_to_reconsider="Fine-tune only if you need a specific response style (then use Both)"
        )

    if scenario.task_type == "factual_qa" and not scenario.data_is_proprietary:
        return FineTuneDecision(
            recommendation="RAG",
            confidence="High",
            primary_reason="Factual Q&A over a document corpus is RAG's sweet spot",
            pros=["Sources are cited and verifiable", "Easy to update knowledge", "No GPU needed"],
            cons=["Slower than fine-tuned model (retrieval step)", "Quality depends on retrieval accuracy"],
            when_to_reconsider="Fine-tune if you need the model to always respond in a very specific format"
        )

    # Hard fine-tune signals
    if scenario.task_type in ("style", "classification") and scenario.labeled_examples >= 500:
        return FineTuneDecision(
            recommendation="Fine-tune",
            confidence="High",
            primary_reason=f"Style transfer and classification with {scenario.labeled_examples}+ examples are ideal for fine-tuning",
            pros=["Consistent output style", "Fast inference (no retrieval)", "No retrieval errors"],
            cons=["Needs labeled data", "Expensive to retrain when requirements change", "GPU required"],
            when_to_reconsider="Switch to RAG if the target style/categories change frequently"
        )

    if scenario.latency_critical and not scenario.knowledge_changes_frequently:
        return FineTuneDecision(
            recommendation="Fine-tune",
            confidence="Medium",
            primary_reason="Latency-critical applications can't afford the retrieval step overhead",
            pros=["Sub-200ms responses possible", "Predictable latency", "No vector DB dependency"],
            cons=["Static knowledge", "Requires training data and GPU"],
            when_to_reconsider="Use RAG if knowledge freshness matters more than latency"
        )

    # Both signals
    if scenario.data_is_proprietary and scenario.labeled_examples >= 100:
        return FineTuneDecision(
            recommendation="Both",
            confidence="Medium",
            primary_reason="Proprietary data + style requirements → fine-tune the style, RAG for knowledge",
            pros=["Best of both worlds", "Consistent brand voice + up-to-date knowledge"],
            cons=["Most complex to build and maintain", "Highest cost"],
            when_to_reconsider="Start with RAG only; add fine-tuning once RAG is validated"
        )

    # Insufficient data
    if scenario.labeled_examples < 100:
        return FineTuneDecision(
            recommendation="RAG",
            confidence="Medium",
            primary_reason=f"Only {scenario.labeled_examples} examples — fine-tuning needs 500+ for reliable results",
            pros=["Works without labeled training data", "Quick to set up"],
            cons=["Quality depends on document coverage"],
            when_to_reconsider="Collect more labeled examples; revisit fine-tuning at 500+"
        )

    # Default
    return FineTuneDecision(
        recommendation="RAG",
        confidence="Low",
        primary_reason="Unclear signals — RAG is the lower-risk starting point",
        pros=["Easier to iterate and update", "No training infrastructure needed"],
        cons=["May not match fine-tuned quality for specialized tasks"],
        when_to_reconsider="Evaluate outputs after 4 weeks; fine-tune if quality is insufficient"
    )


PRESET_SCENARIOS: dict[str, FineTuneScenario] = {
    "Customer support chatbot": FineTuneScenario(
        labeled_examples=200,
        data_is_proprietary=True,
        task_type="domain_knowledge",
        knowledge_changes_frequently=True,
        latency_critical=False,
        gpu_available=False,
        budget_monthly_usd=500.0,
        need_explainability=False,
    ),
    "Legal document classifier": FineTuneScenario(
        labeled_examples=1500,
        data_is_proprietary=True,
        task_type="classification",
        knowledge_changes_frequently=False,
        latency_critical=False,
        gpu_available=True,
        budget_monthly_usd=2000.0,
        need_explainability=True,
    ),
    "Medical Q&A assistant": FineTuneScenario(
        labeled_examples=50,
        data_is_proprietary=False,
        task_type="factual_qa",
        knowledge_changes_frequently=True,
        latency_critical=False,
        gpu_available=False,
        budget_monthly_usd=300.0,
        need_explainability=True,
    ),
    "Content style rewriter": FineTuneScenario(
        labeled_examples=800,
        data_is_proprietary=False,
        task_type="style",
        knowledge_changes_frequently=False,
        latency_critical=True,
        gpu_available=True,
        budget_monthly_usd=1000.0,
        need_explainability=False,
    ),
}
