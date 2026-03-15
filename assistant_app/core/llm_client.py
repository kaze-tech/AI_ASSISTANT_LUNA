from __future__ import annotations

import json

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
        self.session = requests.Session()

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

    def generate_stream(self, prompt: str):
        if self.api_type == "openai":
            yield from self._generate_openai_stream(prompt)
            return
        if self.api_type == "ollama":
            yield from self._generate_ollama_stream(prompt)
            return

        try:
            yield from self._generate_ollama_stream(prompt)
            return
        except Exception:
            pass

        yield from self._generate_openai_stream(prompt)

    def _generate_ollama(self, prompt: str) -> str:
        url = f"{self.base_url}{self.generate_path}"
        response = self.session.post(
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
        fallback = self.session.post(
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

    def _generate_ollama_stream(self, prompt: str):
        url = f"{self.base_url}{self.generate_path}"
        with self.session.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_predict": self.max_tokens,
                    "temperature": self.temperature,
                },
            },
            timeout=120,
            stream=True,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                payload = json.loads(line)
                chunk = payload.get("response", "")
                if chunk:
                    yield chunk

    def _generate_openai_stream(self, prompt: str):
        fallback_url = f"{self.base_url}/v1/chat/completions"
        with self.session.post(
            fallback_url,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True,
            },
            timeout=120,
            stream=True,
        ) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break

                payload = json.loads(data)
                choices = payload.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                chunk = delta.get("content", "")
                if isinstance(chunk, list):
                    chunk = "".join(
                        item.get("text", "")
                        for item in chunk
                        if isinstance(item, dict)
                    )
                if chunk:
                    yield chunk

    def close(self) -> None:
        self.session.close()
