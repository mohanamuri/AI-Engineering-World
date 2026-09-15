"""
03_llm_production_wrapper.py - Production Wrapper with Retry + Rate Limiting
=============================================================================
MUST REMEMBER:
✓ Exponential backoff: wait 1s, 2s, 4s...
✓ Rate limits: respect API headers
✓ Caching: hash prompt to create key
✓ Logging: record all requests

KEY: Retry logic, rate limiting, caching, logging
"""

from anthropic import Anthropic, RateLimitError
import time
import hashlib

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class ProductionLLM:
    """Production-grade LLM wrapper"""

    def __init__(self, max_retries=3, initial_backoff=1.0):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.cache = {}
        self.request_log = []

    def _hash_prompt(self, prompt: str) -> str:
        """Create cache key from prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()

    def call_with_retry(self, prompt: str) -> str:
        """Call LLM with automatic retry and caching"""

        # Step 1: Check cache
        cache_key = self._hash_prompt(prompt)
        if cache_key in self.cache:
            print("📦 Cache hit!")
            self.request_log.append({"status": "cache_hit"})
            return self.cache[cache_key]

        # Step 2: Retry loop
        backoff = self.initial_backoff
        last_error = None

        for attempt in range(self.max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{self.max_retries}")

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )

                result = response.content[0].text

                # MUST REMEMBER: Cache successful response
                self.cache[cache_key] = result
                self.request_log.append({"status": "success"})

                return result

            except RateLimitError as e:
                last_error = e
                print(f"⚠️ Rate limited. Waiting {backoff}s...")
                time.sleep(backoff)
                backoff *= 2

            except Exception as e:
                print(f"❌ Error: {e}")
                raise

        raise RuntimeError(f"Max retries exceeded. Last: {last_error}")

    def get_stats(self) -> dict:
        """Return usage statistics"""
        return {
            "cache_size": len(self.cache),
            "total_requests": len(self.request_log)
        }


def main():
    print("=" * 60)
    print("03: PRODUCTION LLM WRAPPER")
    print("=" * 60)

    llm = ProductionLLM(max_retries=3)

    # Example 1: Caching
    print("\n📝 Example 1: Request with Caching")
    print("-" * 40)
    prompt = "What is machine learning?"

    print("\n🔹 First call (API):")
    response1 = llm.call_with_retry(prompt)
    print(f"Response: {response1[:80]}...")

    print("\n🔹 Second call (cached):")
    response2 = llm.call_with_retry(prompt)
    print(f"Response: {response2[:80]}...")

    # Example 2: Different prompts
    print("\n\n📝 Example 2: Multiple Requests")
    print("-" * 40)
    prompts = ["Explain neural networks", "What is RAG?"]
    for p in prompts:
        try:
            result = llm.call_with_retry(p)
            print(f"✅ {p[:30]}... -> {len(result)} chars")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Example 3: Stats
    print("\n\n📝 Example 3: Statistics")
    print("-" * 40)
    stats = llm.get_stats()
    print(f"✅ Cache size: {stats['cache_size']}")
    print(f"   Total requests: {stats['total_requests']}")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. RETRY: Exponential backoff (1s, 2s, 4s...)
2. RATE LIMIT: Respect API headers, wait appropriately
3. CACHE: Hash prompt to create key, set TTL
4. LOGGING: Record all requests for debugging
5. PRODUCTION: Add error alerts and monitoring
    """)


if __name__ == "__main__":
    main()
