"""
LLM chains with LangChain.

LangChain chains compose multiple steps (retrieval -> prompt -> LLM -> parsing)
into a single interface. This is where orchestration happens.
"""

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.generation.prompt import (
    get_chat_rag_prompt,
    format_context,
    SYSTEM_PROMPT,
)


class RAGChain:
    """
    Production RAG chain using LangChain.

    This is the main orchestrator:
    1. Takes a question
    2. Retrieves relevant documents
    3. Builds a context-aware prompt
    4. Calls the LLM
    5. Returns grounded answer
    """

    def __init__(self, retriever):
        """
        Initialize the RAG chain.

        Args:
            retriever: LangChain retriever instance (with reranking applied)
        """
        settings = get_settings()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.openai_chat_model,
            temperature=0,  # Deterministic for consistency
            api_key=settings.openai_api_key,
            max_retries=3,
        )

        self.retriever = retriever

        # Build the chain
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # "stuff" = put all docs in context (simple, good for small sets)
            retriever=retriever,
            return_source_documents=True,  # Return retrieved docs for citations
            verbose=True,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def generate(self, question: str, documents: list[Document]) -> str:
        """
        Generate an answer given a question and retrieved documents.

        This is called after retrieval and reranking are done.

        Args:
            question: User's question
            documents: Retrieved and reranked documents

        Returns:
            Generated answer string
        """
        # Format context from documents
        context = format_context(documents)

        # Build prompt with context and question
        prompt = get_chat_rag_prompt().format_messages(
            context=context,
            question=question,
        )

        # Call LLM
        response = self.llm.invoke(prompt)

        return response.content or ""

    def invoke_chain(self, question: str) -> dict:
        """
        Full pipeline: retrieve + generate.

        This is the high-level interface for the RAG chain.
        In the API, we use this after security checks.

        Args:
            question: User question

        Returns:
            Dict with 'result' (answer) and 'source_documents'
        """
        return self.chain.invoke({"query": question})
