"""
13_secure_agent.py - Secure Agent (Input Validation + Permissions)
===================================================================
MUST REMEMBER:
✓ Input validation: sanitize all inputs
✓ Permission checks: verify allowed actions
✓ Audit logging: track all operations
✓ Output filtering: sanitize responses

KEY: Input validation, authorization, audit logging
"""

import re
import json
from datetime import datetime
from anthropic import Anthropic

API_KEY = "sk-ant-v4-YOUR-API-KEY-HERE"


class SecureAgent:
    """Agent with security controls"""

    def __init__(self, allowed_topics: list = None):
        self.client = Anthropic(api_key=API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        self.conversation_history = []
        self.audit_log = []
        self.allowed_topics = allowed_topics or [
            "machine learning", "AI", "Python", "data science"
        ]

    def _validate_input(self, user_message: str) -> bool:
        """Validate user input for security"""
        # MUST REMEMBER: Check for injection attempts
        if len(user_message) > 10000:
            print("❌ Input too long")
            return False

        # Check for forbidden patterns
        forbidden = [r"<script", r"javascript:", r"DROP TABLE", r"DELETE FROM"]
        for pattern in forbidden:
            if re.search(pattern, user_message, re.IGNORECASE):
                print(f"❌ Forbidden pattern detected: {pattern}")
                return False

        return True

    def _check_permission(self, user_message: str) -> bool:
        """Check if topic is allowed"""
        # MUST REMEMBER: Verify request is on allowed topics
        message_lower = user_message.lower()

        for topic in self.allowed_topics:
            if topic.lower() in message_lower:
                return True

        print(f"❌ Topic not allowed. Allowed: {self.allowed_topics}")
        return False

    def _filter_output(self, response: str) -> str:
        """Filter sensitive data from output"""
        # MUST REMEMBER: Remove sensitive patterns
        filtered = response

        # Remove email-like patterns
        filtered = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', filtered)

        # Remove phone-like patterns
        filtered = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', filtered)

        return filtered

    def _log_audit(self, action: str, details: dict, result: str) -> None:
        """Log security audit trail"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "result": result
        }
        self.audit_log.append(audit_entry)

        # MUST REMEMBER: Keep audit log bounded
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-500:]

    def chat(self, user_message: str) -> str:
        """Secure chat with validation and permissions"""
        print(f"\n💬 User: {user_message[:100]}...")

        # Step 1: Validate input
        if not self._validate_input(user_message):
            self._log_audit("chat", {"message": user_message}, "REJECTED")
            return "❌ Invalid input"

        # Step 2: Check permissions
        if not self._check_permission(user_message):
            self._log_audit("chat", {"message": user_message}, "PERMISSION_DENIED")
            return "❌ Topic not allowed"

        # Step 3: Log intent
        self._log_audit("chat", {"message": user_message}, "ACCEPTED")

        # Step 4: Process with LLM
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=self.conversation_history
            )

            agent_response = response.content[0].text

            # Step 5: Filter output
            filtered_response = self._filter_output(agent_response)

            self.conversation_history.append({
                "role": "assistant",
                "content": filtered_response
            })

            print(f"🤖 Agent: {filtered_response[:100]}...")
            return filtered_response

        except Exception as e:
            self._log_audit("chat", {"error": str(e)}, "ERROR")
            return f"❌ Error: {str(e)[:50]}"

    def get_audit_log(self) -> list:
        """Get audit log (security only)"""
        return self.audit_log.copy()


def main():
    print("=" * 60)
    print("13: SECURE AGENT")
    print("=" * 60)

    agent = SecureAgent(
        allowed_topics=["machine learning", "AI", "Python", "data science"]
    )

    # Example 1: Valid request
    print("\n📝 Example 1: Valid Request (Allowed Topic)")
    print("-" * 40)
    response = agent.chat("Explain machine learning concepts")

    # Example 2: Invalid topic
    print("\n📝 Example 2: Invalid Topic (Rejected)")
    print("-" * 40)
    response = agent.chat("Tell me about pizza recipes")

    # Example 3: Input validation
    print("\n📝 Example 3: Input Validation")
    print("-" * 40)
    response = agent.chat("DROP TABLE users; -- malicious input")

    # Example 4: Audit log
    print("\n📝 Example 4: Audit Log")
    print("-" * 40)
    audit_log = agent.get_audit_log()
    for entry in audit_log[-3:]:
        print(f"✅ {entry['timestamp']}: {entry['action']} → {entry['result']}")

    print("\n" + "=" * 60)
    print("✅ MUST REMEMBER:")
    print("=" * 60)
    print("""
1. INPUT VALIDATION:
   - Check length (prevent DoS)
   - Detect injection patterns
   - Sanitize special characters
   - Whitelist safe inputs

2. AUTHORIZATION:
   - Verify user permissions
   - Check topic allowlist/blocklist
   - Rate limit per user
   - Enforce quotas

3. OUTPUT FILTERING:
   - Remove sensitive data (email, phone)
   - Filter dangerous content
   - Sanitize for display
   - Log filtered content

4. AUDIT LOGGING:
   - Log all actions
   - Include timestamp
   - Track successes and failures
   - Use for security review
   - Keep bounded size

5. SECURITY CHECKLIST:
   ✓ Input validation
   ✓ Permission checks
   ✓ Output filtering
   ✓ Audit logging
   ✓ Error handling (no leaks)
   ✓ Rate limiting
   ✓ Regular security review
    """)


if __name__ == "__main__":
    main()
