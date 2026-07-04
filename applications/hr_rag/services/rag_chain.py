"""RAG chain service for the HR Analytics policy assistant.

The pipeline:
  1. Retrieve top-k relevant chunks from ChromaDB.
  2. Build context block.
  3. Send prompt to Groq LLM (llama-3.1-8b-instant).
  4. Return answer + source chunks.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import os

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from applications.hr_rag.services.vector_store import similarity_search


def _get_groq_api_key() -> str:
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")


@dataclass
class RAGConfig:
    llm_model: str = "llama-3.1-8b-instant"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 4
    temperature: float = 0.0


@dataclass
class RAGResult:
    query: str
    answer: str
    source_chunks: list[str] = field(default_factory=list)
    context_used: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


_SYSTEM_PROMPT = (
    "You are a precise HR policy assistant. "
    "Answer the question using ONLY the HR policy context provided below. "
    "If the answer is not in the context, say exactly: "
    "'I could not find that information in the provided HR policy document.' "
    "Do not make up information. Be concise and factual."
)

_HUMAN_TEMPLATE = """\
HR policy context:
{context}

Question: {question}

Answer (based only on the context above):"""

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_PROMPT),
    ("human", _HUMAN_TEMPLATE),
])


def run_rag_query(query: str, vectorstore, config: RAGConfig) -> RAGResult:
    docs: list[Document] = similarity_search(vectorstore, query, k=config.top_k)
    context_parts = [doc.page_content for doc in docs]
    context = "\n\n---\n\n".join(context_parts)

    llm = ChatGroq(model=config.llm_model, temperature=config.temperature, api_key=_get_groq_api_key())
    chain = _PROMPT | llm
    response = chain.invoke({"context": context, "question": query})
    answer = response.content if hasattr(response, "content") else str(response)

    return RAGResult(query=query, answer=answer.strip(), source_chunks=context_parts, context_used=context)
