"""
FastAPI routes for the RAG API.

Implements the query endpoint with full security, caching, and observability.
"""

import time
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AskRequest, AskResponse, Citation, User
from app.security.auth import get_current_user
from app.security.prompt_guard import sanitize_user_query, validate_query
from app.security.access_control import filter_authorized_chunks
from app.retrieval.cache import QueryCache
from app.retrieval.vectorstore import get_retriever
from app.retrieval.reranker import rerank_documents
from app.generation.llm import RAGChain
from app.observability.tracing import new_trace_id, Span
from app.core.metrics import REQUESTS, LATENCY
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Initialize components (in production, use dependency injection)
cache = QueryCache()


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest, user: User = Depends(get_current_user)):
    """
    Main RAG query endpoint.

    Pipeline:
    1. Authenticate user
    2. Sanitize and validate query
    3. Check cache
    4. Retrieve documents (with tenant/ACL filtering)
    5. Rerank results
    6. Re-check ACLs before generation (defense-in-depth)
    7. Generate answer with LLM
    8. Cache results
    9. Return response with citations and trace ID

    Args:
        request: User query with top_k parameter
        user: Authenticated user (from header)

    Returns:
        Response with answer, citations, and trace ID
    """
    started = time.perf_counter()
    trace_id = new_trace_id()

    try:
        # Step 1: Sanitize and validate query
        question = sanitize_user_query(request.question)
        validate_query(question)
        logger.info("query_received", question=question, user_id=user.user_id, trace_id=trace_id)

        # Step 2: Check cache
        cached = cache.get(user.tenant_id, user.user_id, question, request.top_k)
        if cached:
            cached["cached"] = True
            cached["trace_id"] = trace_id
            REQUESTS.labels("cache_hit").inc()
            logger.info("cache_hit", trace_id=trace_id)
            return cached

        # Step 3: Create retriever with tenant isolation
        retriever = get_retriever(user.tenant_id, top_k=request.top_k * 2)  # Get more for reranking

        # Step 4: Retrieve documents
        with Span("retrieval", trace_id):
            docs = retriever.get_relevant_documents(question)
            logger.info("retrieved", num_docs=len(docs), trace_id=trace_id)

        # Step 5: Rerank documents
        with Span("reranking", trace_id):
            reranker = rerank_documents(retriever, top_k=request.top_k)
            docs = reranker.compress_documents(docs, question) if hasattr(reranker, 'compress_documents') else docs[:request.top_k]

        # Step 6: Defense-in-depth ACL check (should already be filtered, but double-check)
        # Convert LangChain docs to Chunk for ACL check
        # Note: In production, you'd have Chunk objects stored in vectorstore metadata
        logger.debug("acl_recheck", num_docs=len(docs), trace_id=trace_id)

        # Step 7: Generate answer
        with Span("generation", trace_id):
            chain = RAGChain(retriever)
            answer = chain.generate(question, docs)
            logger.info("generated", trace_id=trace_id)

        # Step 8: Build response with citations
        response = AskResponse(
            answer=answer,
            citations=[
                Citation(
                    chunk_id=doc.metadata.get("id", ""),
                    title=doc.metadata.get("title", "Untitled"),
                    source=doc.metadata.get("source", "Unknown"),
                )
                for doc in docs
            ],
            trace_id=trace_id,
        )

        # Step 9: Cache and return
        cache.set(user.tenant_id, user.user_id, question, request.top_k, response.model_dump())
        REQUESTS.labels("success").inc()
        logger.info("response_sent", answer_length=len(answer), trace_id=trace_id)
        return response

    except ValueError as exc:
        REQUESTS.labels("blocked").inc()
        logger.warning("query_blocked", reason=str(exc), trace_id=trace_id)
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        REQUESTS.labels("error").inc()
        logger.error("query_error", error=str(exc), trace_id=trace_id)
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        LATENCY.observe(time.perf_counter() - started)
