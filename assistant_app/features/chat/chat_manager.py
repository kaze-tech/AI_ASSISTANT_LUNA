from __future__ import annotations

from assistant_app.core.llm_client import LLMClient


class ChatManager:
    def __init__(self, llm_client: LLMClient, system_prompt: str) -> None:
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.history: list[tuple[str, str]] = []
        self.max_history_turns = 4

    def ask(self, user_text: str) -> str:
        self.history.append(("user", user_text))

        recent_turns = self.history[-self.max_history_turns :]
        transcript = "\n".join(f"{role}: {content}" for role, content in recent_turns)
        prompt = f"{self.system_prompt}\n\nConversation:\n{transcript}\nassistant:"

        reply = self.llm_client.generate(prompt)
        self.history.append(("assistant", reply))
        return reply
