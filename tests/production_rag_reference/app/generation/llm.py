from openai import OpenAI
from app.core.config import get_settings
from tenacity import retry, stop_after_attempt, wait_exponential
from app.generation.prompt import SYSTEM_PROMPT

class LLM:
    def __init__(self):
        s = get_settings()
        self.client = OpenAI(api_key=s.openai_api_key)
        self.model = s.openai_chat_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""
