from __future__ import annotations

from dataclasses import dataclass
import os
import webbrowser

from assistant_app.core.media_keys import press_media_play_pause


@dataclass
class CommandResult:
    handled: bool
    message: str = ""
    needs_confirmation: bool = False
    confirm_action: str | None = None


class CommandRouter:
    def route(self, text: str) -> CommandResult:
        lowered = text.lower().strip()

        if "open youtube" in lowered:
            webbrowser.open("https://www.youtube.com")
            return CommandResult(True, "Opening YouTube.")

        if any(k in lowered for k in ["play music", "pause music", "play pause", "toggle music"]):
            press_media_play_pause()
            return CommandResult(True, "Toggled play/pause.")

        if any(k in lowered for k in ["power off", "shut down", "shutdown pc", "turn off pc"]):
            return CommandResult(
                handled=True,
                message="Power off requested. Please confirm.",
                needs_confirmation=True,
                confirm_action="shutdown",
            )

        return CommandResult(False)

    @staticmethod
    def run_confirmed_action(action: str) -> str:
        if action == "shutdown":
            os.system("shutdown /s /t 0")
            return "Shutting down now."
        return "No action executed."
