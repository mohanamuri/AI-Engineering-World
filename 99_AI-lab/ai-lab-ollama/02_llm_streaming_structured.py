"""
02_llm_streaming_structured.py - Streaming + Structured Output
===============================================================
MUST REMEMBER:
✓ Streaming = real-time response (good for UX)
✓ Use json_schema for guaranteed JSON structure
✓ Always validate parsed JSON
✓ Handle stream disconnection gracefully

KEY CONCEPTS:
- stream=True enables token streaming
- json_schema parameter ensures valid JSON
- Real-time vs batch trade-offs
"""

from anthropic import Anthropic
import json
from pydantic import BaseModel, Field

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class PersonInfo(BaseModel):
    """Structured output for person extraction"""
    name: str = Field(description="Person's full name")
    age: int = Field(description="Age in years")
    profession: str = Field(description="Job title")
    skills: list[str] = Field(description="List of key skills")


class StreamingLLM:
    """LLM with streaming and structured output"""

    def __init__(self):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    def stream_response(self, prompt: str):
        """Stream response token-by-token"""
        print("\n🔄 Streaming: ", end="")
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    yield text
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise

    def get_structured_output(self, prompt: str, response_type):
        """Get response in strict JSON format"""
        schema = response_type.model_json_schema()

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_type.__name__,
                        "schema": schema,
                        "strict": True
                    }
                }
            )

            response_text = response.content[0].text
            parsed = json.loads(response_text)
            return parsed

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            raise


def main():
    print("=" * 60)
    print("02: LLM STREAMING + STRUCTURED OUTPUT")
    print("=" * 60)

    llm = StreamingLLM()

    # Example 1: Basic streaming
    print("\n📝 Example 1: Token-by-Token Streaming")
    print("-" * 40)
    response = ""
    for token in llm.stream_response("Explain quantum computing in 50 words"):
        response += token
    print(f"\n✅ Received {len(response)} chars")

    # Example 2: Structured output
    print("\n\n📝 Example 2: Structured JSON Output")
    print("-" * 40)
    result = llm.get_structured_output(
        prompt="Extract: Albert Einstein was a physicist born 1879, expert in relativity",
        response_type=PersonInfo
    )
    print(f"✅ Name: {result['name']}")
    print(f"   Age: {result['age']}")
    print(f"   Profession: {result['profession']}")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. STREAMING: Use with stream() context manager
2. STRUCTURED: Always use json_schema, set strict=True
3. VALIDATION: Always parse JSON after response
4. FALLBACK: Have fallback if LLM fails
    """)


if __name__ == "__main__":
    main()
