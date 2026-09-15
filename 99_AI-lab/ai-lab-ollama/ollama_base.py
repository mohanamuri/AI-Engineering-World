"""
ollama_base.py - Ollama Base Client (Shared across all examples)

Use this as base for all Ollama-based scripts.
No API key needed, runs locally on http://localhost:11434
"""

import requests
import json


class OllamaClient:
    """Unified Ollama client for all examples"""

    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client

        Args:
            model: Model to use (mistral, neural-chat, llama2)
            base_url: Ollama server URL (default: local)
        """
        self.model = model
        self.base_url = base_url
        self.chat_endpoint = f"{base_url}/api/chat"
        self.generate_endpoint = f"{base_url}/api/generate"

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """
        Send chat messages and get response

        Args:
            messages: List of messages with role and content
            temperature: 0-1 (randomness)
            max_tokens: Max response length

        Returns:
            Response text
        """
        try:
            response = requests.post(
                self.chat_endpoint,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=300  # Long timeout for Ollama
            )

            if response.status_code != 200:
                raise Exception(f"Ollama error ({response.status_code}): {response.text}")

            result = response.json()
            return result["message"]["content"]

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "\n❌ Can't connect to Ollama!\n"
                "Make sure Ollama is running:\n"
                "  1. ollama serve\n"
                "  2. Keep this terminal open\n"
                "  3. Run this script in another terminal"
            )

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Simple text generation (non-chat)

        Args:
            prompt: Text prompt
            temperature: 0-1 (randomness)

        Returns:
            Generated text
        """
        try:
            response = requests.post(
                self.generate_endpoint,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=300
            )

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")

            result = response.json()
            return result["response"]

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "\n❌ Can't connect to Ollama!\n"
                "Make sure Ollama is running:\n"
                "  1. ollama serve\n"
                "  2. Keep this terminal open\n"
                "  3. Run this script in another terminal"
            )

    def list_models(self) -> list:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
        except:
            return []


def check_ollama_setup():
    """Check if Ollama is properly set up"""
    try:
        client = OllamaClient()
        models = client.list_models()

        if not models:
            print("\n⚠️  No models found!")
            print("Download one with:")
            print("  ollama pull mistral")
            return False

        print(f"✅ Ollama found with {len(models)} model(s)")
        print(f"   Models: {', '.join(models)}")
        return True

    except ConnectionError:
        print("\n❌ Ollama not running!")
        print("Start it with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
