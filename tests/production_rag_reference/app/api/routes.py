import time
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AskRequest, AskResponse, Citation, User
from app.security.auth import get_current_user
from app.security.prompt_guard import sanitize_user_query, validate_query
from app.security.access_control import filter_authorized_chunks
from app.retrieval.cache import QueryCache
from app.generation.prompt import build_prompt
from app.generation.llm import LLM
from app.observability.tracing import new_trace_id, Span
from app.core.metrics import REQUESTS, LATENCY

router = APIRouter()
cache = QueryCache()
llm = LLM()

def retrieve_for_user(question: str, user: User):
    """
    Integration point for:
      1. metadata/tenant filter
      2. dense vector search
      3. BM25 search
      4. RRF
      5. cross-encoder reranking

    This intentionally raises until connected to your chosen vector database.
    """
    raise NotImplementedError("Connect pgvector/OpenSearch/etc. here.")

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest, user: User = Depends(get_current_user)):
    started = time.perf_counter()
    trace_id = new_trace_id()
    try:
        question = sanitize_user_query(request.question)
        validate_query(question)

        cached = cache.get(user.tenant_id, user.user_id, question, request.top_k)
        if cached:
            cached["cached"] = True
            cached["trace_id"] = trace_id
            REQUESTS.labels("cache_hit").inc()
            return cached

        with Span("retrieval", trace_id):
            results = retrieve_for_user(question, user)

        # Defense-in-depth authorization immediately before LLM exposure.
        allowed = set(c.id for c in filter_authorized_chunks(
            [r.chunk for r in results], user
        ))
        results = [r for r in results if r.chunk.id in allowed]

        context = [
            {"title": r.chunk.title, "source": r.chunk.source, "text": r.chunk.text}
            for r in results
        ]

        with Span("generation", trace_id):
            answer = llm.generate(build_prompt(question, context))

        response = AskResponse(
            answer=answer,
            citations=[
                Citation(chunk_id=r.chunk.id, title=r.chunk.title, source=r.chunk.source)
                for r in results
            ],
            trace_id=trace_id,
        )
        cache.set(user.tenant_id, user.user_id, question, request.top_k, response.model_dump())
        REQUESTS.labels("success").inc()
        return response

    except ValueError as exc:
        REQUESTS.labels("blocked").inc()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        LATENCY.observe(time.perf_counter() - started)
