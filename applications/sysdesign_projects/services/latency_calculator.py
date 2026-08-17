"""Latency budget calculator for RAG + LLM systems."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class LatencyBudget:
    # Input
    network_in_ms: float = 20.0        # client → server round-trip start
    embedding_ms: float = 15.0         # query embedding
    vector_search_ms: float = 30.0     # ChromaDB/Pinecone search
    reranking_ms: float = 0.0          # optional reranker model
    context_prep_ms: float = 5.0       # format context into prompt
    llm_ttft_ms: float = 300.0         # time to first token
    llm_generation_ms: float = 1200.0  # full generation (non-streaming)
    post_process_ms: float = 10.0      # parse / format response
    network_out_ms: float = 20.0       # server → client

    @property
    def total_ms(self) -> float:
        return (
            self.network_in_ms + self.embedding_ms + self.vector_search_ms +
            self.reranking_ms + self.context_prep_ms + self.llm_ttft_ms +
            self.llm_generation_ms + self.post_process_ms + self.network_out_ms
        )

    @property
    def total_with_streaming_ms(self) -> float:
        """With streaming, perceived latency = TTFT (user sees first token immediately)."""
        return (
            self.network_in_ms + self.embedding_ms + self.vector_search_ms +
            self.reranking_ms + self.context_prep_ms + self.llm_ttft_ms +
            self.post_process_ms + self.network_out_ms
        )

    @property
    def bottleneck(self) -> str:
        components = {
            "LLM Generation": self.llm_generation_ms,
            "LLM TTFT": self.llm_ttft_ms,
            "Vector Search": self.vector_search_ms,
            "Reranking": self.reranking_ms,
            "Embedding": self.embedding_ms,
            "Network (in)": self.network_in_ms,
            "Network (out)": self.network_out_ms,
            "Context Prep": self.context_prep_ms,
            "Post-process": self.post_process_ms,
        }
        return max(components, key=components.get)

    @property
    def llm_pct(self) -> float:
        return (self.llm_ttft_ms + self.llm_generation_ms) / self.total_ms * 100

    def breakdown(self) -> list[dict]:
        """Return ordered breakdown for waterfall chart."""
        return [
            {"stage": "Network (in)", "ms": self.network_in_ms, "category": "Infrastructure"},
            {"stage": "Embedding", "ms": self.embedding_ms, "category": "ML"},
            {"stage": "Vector Search", "ms": self.vector_search_ms, "category": "Retrieval"},
            {"stage": "Reranking", "ms": self.reranking_ms, "category": "ML"},
            {"stage": "Context Prep", "ms": self.context_prep_ms, "category": "Infrastructure"},
            {"stage": "LLM TTFT", "ms": self.llm_ttft_ms, "category": "LLM"},
            {"stage": "LLM Generation", "ms": self.llm_generation_ms, "category": "LLM"},
            {"stage": "Post-process", "ms": self.post_process_ms, "category": "Infrastructure"},
            {"stage": "Network (out)", "ms": self.network_out_ms, "category": "Infrastructure"},
        ]


PRESET_CONFIGS = {
    "Simple chatbot (no RAG)": LatencyBudget(
        network_in_ms=20, embedding_ms=0, vector_search_ms=0, reranking_ms=0,
        context_prep_ms=2, llm_ttft_ms=250, llm_generation_ms=1000,
        post_process_ms=5, network_out_ms=20,
    ),
    "Basic RAG (ChromaDB)": LatencyBudget(
        network_in_ms=20, embedding_ms=15, vector_search_ms=30, reranking_ms=0,
        context_prep_ms=5, llm_ttft_ms=300, llm_generation_ms=1200,
        post_process_ms=10, network_out_ms=20,
    ),
    "Production RAG (Pinecone + reranker)": LatencyBudget(
        network_in_ms=15, embedding_ms=12, vector_search_ms=20, reranking_ms=80,
        context_prep_ms=5, llm_ttft_ms=280, llm_generation_ms=1100,
        post_process_ms=10, network_out_ms=15,
    ),
    "Enterprise RAG (multi-hop + cache)": LatencyBudget(
        network_in_ms=10, embedding_ms=10, vector_search_ms=15, reranking_ms=60,
        context_prep_ms=15, llm_ttft_ms=200, llm_generation_ms=800,
        post_process_ms=10, network_out_ms=10,
    ),
}
