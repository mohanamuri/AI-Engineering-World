"""
RAG chain service for the loan eligibility assistant.

The pipeline:
  1. Retrieve the top-k relevant chunks from ChromaDB.
  2. Format them into a context block.
  3. Send a structured prompt (context + question) to the Ollama LLM.
  4. Return the answer plus the source chunks used.

Why separate retrieval from generation?
-----------------------------------------
In production you monitor each step independently:
  - Retrieval quality: measured by recall@k (did the right chunk appear?)
  - Generation quality: measured by faithfulness (did the LLM stay grounded?)
Keeping them separate lets you swap the retriever or the LLM without
touching the other.

Why "answer only from the context"?
--------------------------------------
LLMs hallucinate. By restricting answers to the provided context, every
claim can be traced to a specific chunk. This is especially important in
finance where a wrong policy quote could lead to a compliance violation.

Interview note — RAG vs fine-tuning
--------------------------------------
Fine-tuning bakes knowledge into model weights — expensive, slow to update,
and hard to audit. RAG keeps the knowledge external in a database — cheap
to update (re-index), easy to audit (show the retrieved chunks), and works
with any model without retraining.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import os

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from applications.loan_rag.services.vector_store import similarity_search


def _get_groq_api_key() -> str:
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RAGConfig:
    """Tunable parameters for the RAG pipeline."""
    llm_model: str = "compound-beta-mini"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 4
    temperature: float = 0.0


@dataclass
class RAGResult:
    """A single RAG query/response pair."""
    query: str
    answer: str
    source_chunks: list[str] = field(default_factory=list)
    context_used: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are a precise loan policy assistant for FinCorp Bank. "
    "Answer the question using ONLY the policy context provided below. "
    "If the answer is not in the context, say exactly: "
    "'I could not find that information in the provided policy document.' "
    "Do not make up information. Be concise and factual."
)

_HUMAN_TEMPLATE = """\
Policy context:
{context}

Question: {question}

Answer (based only on the context above):"""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_PROMPT),
    ("human", _HUMAN_TEMPLATE),
])


# ---------------------------------------------------------------------------
# RAG runner
# ---------------------------------------------------------------------------

def run_rag_query(
    query: str,
    vectorstore,
    config: RAGConfig,
) -> RAGResult:
    """Run the full RAG pipeline for a single question.

    Steps:
      1. Retrieve top-k chunks from the vector store.
      2. Concatenate chunks into a context block.
      3. Invoke the Ollama LLM with the prompt.
      4. Return a RAGResult with answer + source chunks.

    Args:
        query:       Natural language question from the user.
        vectorstore: Built Chroma instance (from vector_store.build_vector_store).
        config:      RAGConfig controlling model names and k.

    Returns:
        RAGResult with the answer and retrieved source chunks.
    """
    # Step 1 — Retrieve
    docs: list[Document] = similarity_search(vectorstore, query, k=config.top_k)

    # Step 2 — Build context
    context_parts = [doc.page_content for doc in docs]
    context = "\n\n---\n\n".join(context_parts)

    # Step 3 — Generate
    llm = ChatGroq(model=config.llm_model, temperature=config.temperature, api_key=_get_groq_api_key())
    chain = _PROMPT | llm
    response = chain.invoke({"context": context, "question": query})
    answer = response.content if hasattr(response, "content") else str(response)

    return RAGResult(
        query=query,
        answer=answer.strip(),
        source_chunks=context_parts,
        context_used=context,
    )
