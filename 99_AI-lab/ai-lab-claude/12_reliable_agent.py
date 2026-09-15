"""
12_reliable_agent.py - Reliable Agent (Error Handling + Recovery)
=================================================================
MUST REMEMBER:
✓ Retry logic: exponential backoff
✓ Graceful degradation: fallbacks
✓ Error recovery: resume from failure
✓ Monitoring: track reliability metrics

KEY: Error handling, retries, fallbacks, circuit breaker
"""

import time
from anthropic import Anthropic, RateLimitError

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class ReliableAgent:
    """Agent with error handling and recovery"""

    def __init__(self):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_retries = 3
        self.conversation_history = []
        self.error_log = []

    def _execute_with_retry(self, messages, max_retries: int = 3) -> str:
        """Execute with retry logic"""
        backoff = 1.0

        for attempt in range(max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{max_retries}")

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=messages
                )

                return response.content[0].text

            except RateLimitError:
                print(f"⚠️ Rate limited. Waiting {backoff}s...")
                time.sleep(backoff)
                backoff *= 2

            except Exception as e:
                print(f"❌ Error: {e}")
                self.error_log.append({
                    "attempt": attempt,
                    "error": str(e),
                    "timestamp": time.time()
                })

                if attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    raise

        raise RuntimeError("Max retries exceeded")

    def chat(self, user_message: str, use_fallback: bool = True) -> str:
        """Chat with reliability"""
        print(f"\n💬 User: {user_message}")

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            # MUST REMEMBER: Execute with retry logic
            response = self._execute_with_retry(
                self.conversation_history,
                max_retries=self.max_retries
            )

            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })

            print(f"🤖 Agent: {response[:100]}...")
            return response

        except Exception as e:
            print(f"❌ Failed after retries: {e}")

            # MUST REMEMBER: Graceful fallback
            if use_fallback:
                fallback_response = self._get_fallback_response(user_message)
                print(f"📋 Fallback: {fallback_response}")

                self.conversation_history.append({
                    "role": "assistant",
                    "content": fallback_response
                })

                return fallback_response
            else:
                raise

    def _get_fallback_response(self, user_message: str) -> str:
        """Fallback response when API fails"""
        fallbacks = {
            "hello": "Hello! I'm temporarily having issues, but I'm here to help.",
            "how": "I'm experiencing temporary difficulties, but please ask and I'll try.",
            "what": "I'm currently unavailable, but please try again in a moment."
        }

        for keyword, response in fallbacks.items():
            if keyword in user_message.lower():
                return response

        return "I'm experiencing technical difficulties. Please try again later."

    def get_reliability_stats(self) -> dict:
        """Get reliability statistics"""
        return {
            "total_errors": len(self.error_log),
            "successful_calls": len(self.conversation_history) // 2,
            "error_rate": len(self.error_log) / max(len(self.conversation_history), 1)
        }


def main():
    print("=" * 60)
    print("12: RELIABLE AGENT")
    print("=" * 60)

    agent = ReliableAgent()

    # Example 1: Normal chat
    print("\n📝 Example 1: Normal Chat")
    print("-" * 40)
    response = agent.chat("What is machine learning?")

    # Example 2: With potential failure (fallback)
    print("\n📝 Example 2: Chat with Fallback Available")
    print("-" * 40)
    response = agent.chat("Hello there!")

    # Example 3: Stats
    print("\n📝 Example 3: Reliability Stats")
    print("-" * 40)
    stats = agent.get_reliability_stats()
    print(f"✅ Total errors: {stats['total_errors']}")
    print(f"   Successful calls: {stats['successful_calls']}")
    print(f"   Error rate: {stats['error_rate']:.1%}")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. RETRY STRATEGY:
   - Exponential backoff (1s, 2s, 4s...)
   - Only retry transient errors
   - Max retries limit

2. ERROR TYPES:
   - Transient: rate limit, timeout (retry)
   - Permanent: auth, validation (fail fast)
   - Unknown: log and retry once

3. FALLBACK:
   - Cache common responses
   - Provide degraded service
   - Log fallback usage
   - Alert on excessive fallbacks

4. MONITORING:
   - Track error rate
   - Monitor retry distribution
   - Alert on threshold exceeded
   - Log all errors for debugging
    """)


if __name__ == "__main__":
    main()
