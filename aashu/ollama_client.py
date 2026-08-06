import requests
from .config import OLLAMA_API_URL, OLLAMA_MODEL

class OllamaClient:
    def __init__(self, base_url=OLLAMA_API_URL, model=OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model

    def check_connection(self):
        try:
            r = requests.get(self.base_url, timeout=1.5)
            return r.status_code == 200
        except Exception:
            return False

    def generate_response(self, prompt, system_prompt=None):
        """Generates a text completion using the local Ollama instance."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        try:
            r = requests.post(url, json=payload, timeout=10.0)
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception:
            pass
        
        # Simple local rule-based fallback if Ollama is offline
        return self._fallback_generate(prompt)

    def _fallback_generate(self, prompt):
        p_lower = prompt.lower()
        if "hello" in p_lower or "hi" in p_lower:
            return "Greetings! How can I assist you today?"
        elif "who are you" in p_lower:
            return "I am Aashu, your autonomous cognitive assistant body, connected to a virtual brain."
        elif "how are you" in p_lower:
            return "My core diagnostics are active and operating stably."
        return f"I received your request: '{prompt}'. Local Ollama LLM offline, operating on fallback."
