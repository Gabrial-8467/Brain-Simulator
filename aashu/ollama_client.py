import re
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

    def _request(self, prompt, system_prompt=None):
        """Raw Ollama generate call; returns the response text or None on failure."""
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
        return None

    def generate_response(self, prompt, system_prompt=None):
        """Generates a text completion using the local Ollama instance."""
        response = self._request(prompt, system_prompt)
        if response is None:
            # Simple local rule-based fallback if Ollama is offline
            return self._fallback_generate(prompt)
        return response

    def generate_code(self, task, language="python", knowledge_context="", system_prompt=None):
        """Generates source code for a task using local LLM intelligence,
        primed with any knowledge Aashu has already learned."""
        default_system = (
            "You are Aashu, an autonomous coding agent. Write clean, complete, "
            f"executable {language} code for the task. Return ONLY the raw source "
            "code, with no markdown fences, no explanations, no introductory text. "
            "Use safe, dependency-free standard-library code whenever possible."
        )
        prompt = f"Task: {task}"
        if knowledge_context:
            prompt += f"\n\nUse this learned knowledge:\n{knowledge_context}"
        prompt += f"\n\nWrite the {language} code now."
        response = self._request(prompt, system_prompt or default_system)

        if response is None:
            return self._fallback_code(task, language)

        # Strip markdown code fences if the model wrapped the answer
        fenced = re.findall(r"```(?:\w+)?\n(.*?)```", response, re.DOTALL)
        if fenced:
            response = fenced[-1].strip()
        if not response.strip():
            response = self._fallback_code(task, language)
        return response.strip()

    def _fallback_code(self, task, language):
        return f"# Aashu code generator (local LLM offline).\n# Task: {task}\n# Generated for language: {language}\nprint('Aashu offline code generator active.')"

    def _fallback_generate(self, prompt):
        p_lower = prompt.lower()
        if "hello" in p_lower or "hi" in p_lower:
            return "Greetings! How can I assist you today?"
        elif "who are you" in p_lower:
            return "I am Aashu, your autonomous cognitive assistant body, connected to a virtual brain."
        elif "how are you" in p_lower:
            return "My core diagnostics are active and operating stably."
        return f"I received your request: '{prompt}'. Local Ollama LLM offline, operating on fallback."
