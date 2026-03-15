from __future__ import annotations

import requests


class LLMClient:
    def __init__(
        self,
        base_url: str,
        generate_path: str,
        model: str,
        api_type: str = "auto",
        max_tokens: int = 180,
        temperature: float = 0.6,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.generate_path = generate_path
        self.model = model
        self.api_type = (api_type or "auto").lower()
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        if self.api_type == "openai":
            return self._generate_openai(prompt)
        if self.api_type == "ollama":
            return self._generate_ollama(prompt)

        # Primary path: Ollama-style generate API.
        try:
            return self._generate_ollama(prompt)
        except Exception:
            pass

        # Fallback path: OpenAI-compatible chat completions (LM Studio / others).
        return self._generate_openai(prompt)

    def _generate_ollama(self, prompt: str) -> str:
        url = f"{self.base_url}{self.generate_path}"
        response = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": self.max_tokens,
                    "temperature": self.temperature,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("response", "").strip()

    def _generate_openai(self, prompt: str) -> str:
        fallback_url = f"{self.base_url}/v1/chat/completions"
        fallback = requests.post(
            fallback_url,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            timeout=120,
        )
        fallback.raise_for_status()
        payload = fallback.json()
        choices = payload.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "").strip()
