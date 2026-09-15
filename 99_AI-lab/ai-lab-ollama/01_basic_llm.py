"""
01_basic_llm.py - Basic LLM Application
========================================

🎯 HOW TO USE THIS FILE:
========================
For CLAUDE.ai Testing (Manual):
1. Copy the example code from main() function
2. Go to Claude.ai (https://claude.ai)
3. Paste the code and explain what you want to do
4. Claude will help you understand and test it

OR: Run locally with Anthropic API key:
1. Get API key from: https://console.anthropic.com/account/keys
2. Replace API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"
3. Run: python 01_basic_llm.py

WHAT YOU'LL LEARN:
- How to call Claude API
- Basic prompt engineering
- Handling responses
- Error handling basics

MUST REMEMBER:
✓ API Key is hardcoded (replace with your key)
✓ Messages have a specific format: role + content
✓ Always handle rate limits and API errors
✓ Keep prompts clear and specific
✗ DON'T: Commit API keys to git, hardcode in production

KEY CONCEPTS:
- Client initialization
- Message format (role: "user" or "assistant")
- Temperature: controls randomness (0=deterministic, 1=creative)
- Max tokens: limits response length
"""

from anthropic import Anthropic

# MUST REMEMBER: Replace with your actual API key from https://console.anthropic.com/account/keys
API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"  # <- REPLACE THIS WITH YOUR KEY


class BasicLLMApp:
    """Simple LLM chatbot wrapper"""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize the LLM client"""
        self.client = Anthropic(api_key=API_KEY)
        self.model = model
        self.conversation_history = []

    def ask(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Send a prompt and get a response

        Args:
            prompt: Your question/instruction
            temperature: 0.0=predictable, 1.0=creative
        """
        # MUST REMEMBER: Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=temperature,
                messages=self.conversation_history
            )

            assistant_message = response.content[0].text

            # MUST REMEMBER: Add assistant response for multi-turn
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            print(f"❌ API Error: {e}")
            self.conversation_history.pop()
            raise

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []


def main():
    print("=" * 60)
    print("01: BASIC LLM APPLICATION")
    print("=" * 60)

    app = BasicLLMApp()

    # Example 1
    print("\n📝 Example 1: Simple Question")
    print("-" * 40)
    response = app.ask("What is Python and why is it used for AI?")
    print(f"Response: {response[:200]}...")

    # Example 2
    print("\n📝 Example 2: Multi-turn (uses history)")
    print("-" * 40)
    response = app.ask("Can you give me a concrete example?")
    print(f"Response: {response[:200]}...")

    # Example 3
    print("\n📝 Example 3: Creative Mode (temperature=0.9)")
    print("-" * 40)
    app.reset_conversation()
    response = app.ask(
        "Write a short poem about AI",
        temperature=0.9
    )
    print(f"Response:\n{response}")

    # Example 4
    print("\n📝 Example 4: Analytical Mode (temperature=0.2)")
    print("-" * 40)
    app.reset_conversation()
    response = app.ask(
        "What are 3 differences between ML and Deep Learning?",
        temperature=0.2
    )
    print(f"Response:\n{response}")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. Temperature: 0-0.3 (analytical), 0.4-0.7 (balanced), 0.8-1.0 (creative)
2. History: Maintain conversation_history for multi-turn
3. Error: Always wrap API calls in try-except
4. Messages: Keep role (user/assistant) + content structure
5. Reset: Call reset_conversation() when starting new topic
    """)


if __name__ == "__main__":
    main()
