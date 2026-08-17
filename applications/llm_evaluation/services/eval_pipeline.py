"""Eval Pipeline: run full test dataset through all metrics."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from .ragas_eval import RAGASConfig, RAGASResult, run_ragas_eval
from .hallucination import HallucinationConfig, HallucinationResult, detect_hallucination


@dataclass
class PipelineConfig:
    llm_model: str = "openai/gpt-oss-20b"
    temperature: float = 0.0
    run_ragas: bool = True
    run_judge: bool = True
    run_hallucination: bool = True


@dataclass
class TestCase:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    reference_answer: str = ""  # for judge comparison


@dataclass
class CaseResult:
    test_case: TestCase
    ragas: RAGASResult | None = None
    hallucination: HallucinationResult | None = None


@dataclass
class PipelineResult:
    cases: list[CaseResult]
    avg_faithfulness: float = 0.0
    avg_relevance: float = 0.0
    avg_recall: float = 0.0
    avg_precision: float = 0.0
    avg_overall: float = 0.0
    avg_hallucination_rate: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def run_eval_pipeline(
    test_cases: list[TestCase],
    config: PipelineConfig,
    progress_cb=None,
) -> PipelineResult:
    ragas_cfg = RAGASConfig(llm_model=config.llm_model, temperature=config.temperature)
    hall_cfg = HallucinationConfig(llm_model=config.llm_model, temperature=config.temperature)

    results = []
    for i, tc in enumerate(test_cases):
        ragas_result = None
        hall_result = None
        if config.run_ragas:
            ragas_result = run_ragas_eval(
                tc.question, tc.answer, tc.contexts, tc.ground_truth, ragas_cfg
            )
        if config.run_hallucination:
            context_text = "\n".join(tc.contexts)
            hall_result = detect_hallucination(tc.answer, context_text, hall_cfg)
        results.append(CaseResult(test_case=tc, ragas=ragas_result, hallucination=hall_result))
        if progress_cb:
            progress_cb(i + 1, len(test_cases))

    # compute averages
    ragas_results = [r.ragas for r in results if r.ragas]
    hall_results = [r.hallucination for r in results if r.hallucination]

    def avg(lst, key):
        return sum(getattr(x, key) for x in lst) / len(lst) if lst else 0.0

    return PipelineResult(
        cases=results,
        avg_faithfulness=avg(ragas_results, "faithfulness"),
        avg_relevance=avg(ragas_results, "answer_relevance"),
        avg_recall=avg(ragas_results, "context_recall"),
        avg_precision=avg(ragas_results, "context_precision"),
        avg_overall=avg(ragas_results, "overall_score"),
        avg_hallucination_rate=avg(hall_results, "hallucination_rate"),
    )
