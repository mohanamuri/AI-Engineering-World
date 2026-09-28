from openai import OpenAI
from app.core.config import get_settings
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
def embed_texts(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [x.embedding for x in response.data]
