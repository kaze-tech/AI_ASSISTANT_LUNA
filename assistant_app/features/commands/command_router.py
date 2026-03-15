from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import webbrowser

from assistant_app.core.media_keys import press_media_play_pause


@dataclass
class CommandResult:
    handled: bool
    message: str = ""
    needs_confirmation: bool = False
    confirm_action: str | None = None


class CommandRouter:
    GITHUB_URL = "https://github.com"
    GMAIL_URL = "https://mail.google.com"
    YOUTUBE_URL = "https://www.youtube.com"
    INTRO_RESPONSE = (
        "Hello! I'm LUNA, your personal AI assistant created by Joel Jacob, "
        "a Third Year BSc AI & ML student at Sree Narayana Guru College, Coimbatore.\n\n"
        "I can listen to your voice, understand your questions, respond intelligently, "
        "and help you navigate apps through voice commands. I also support gesture-based "
        "media control for a more interactive experience."
    )

    @staticmethod
    def _is_intro_prompt(lowered: str) -> bool:
        intro_phrases = (
            "who are you",
            "introduce yourself",
            "tell me about yourself",
            "tell about yourself",
            "about yourself",
            "what are you",
            "tell me who you are",
            "say something about yourself",
        )
        return any(phrase in lowered for phrase in intro_phrases)

    @staticmethod
    def _find_executable(command_names: tuple[str, ...], extra_paths: tuple[str, ...] = ()) -> str | None:
        for name in command_names:
            resolved = shutil.which(name)
            if resolved:
                return resolved

        for raw_path in extra_paths:
            path = Path(os.path.expandvars(raw_path))
            if path.exists():
                return str(path)

        return None

    @classmethod
    def _find_brave(cls) -> str | None:
        return cls._find_executable(
            ("brave.exe", "brave"),
            (
                r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe",
            ),
        )

    @classmethod
    def _find_spotify(cls) -> str | None:
        return cls._find_executable(
            ("Spotify.exe", "spotify"),
            (
                r"%AppData%\Spotify\Spotify.exe",
                r"%LocalAppData%\Microsoft\WindowsApps\Spotify.exe",
            ),
        )

    @classmethod
    def _find_vscode(cls) -> str | None:
        return cls._find_executable(
            ("code", "code.cmd", "Code.exe"),
            (
                r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe",
                r"%ProgramFiles%\Microsoft VS Code\Code.exe",
                r"%ProgramFiles(x86)%\Microsoft VS Code\Code.exe",
            ),
        )

    @staticmethod
    def _launch_command(command: list[str]) -> bool:
        try:
            subprocess.Popen(command)
            return True
        except OSError:
            return False

    @classmethod
    def _open_url(cls, url: str, label: str) -> CommandResult:
        brave = cls._find_brave()
        if brave and cls._launch_command([brave, url]):
            return CommandResult(True, f"Opening {label} in Brave.")

        webbrowser.open(url)
        return CommandResult(True, f"Opening {label} in your browser.")

    @classmethod
    def _open_brave(cls) -> CommandResult:
        brave = cls._find_brave()
        if brave and cls._launch_command([brave]):
            return CommandResult(True, "Opening Brave.")
        return CommandResult(True, "Brave browser was not found on this PC.")

    @classmethod
    def _open_spotify(cls) -> CommandResult:
        spotify = cls._find_spotify()
        if spotify and cls._launch_command([spotify]):
            return CommandResult(True, "Opening Spotify.")
        return CommandResult(True, "Spotify was not found on this PC.")

    @staticmethod
    def _open_notepad() -> CommandResult:
        if CommandRouter._launch_command(["notepad.exe"]):
            return CommandResult(True, "Opening Notepad.")
        return CommandResult(True, "Notepad could not be opened.")

    @staticmethod
    def _open_calculator() -> CommandResult:
        if CommandRouter._launch_command(["calc.exe"]):
            return CommandResult(True, "Opening Calculator.")
        return CommandResult(True, "Calculator could not be opened.")

    @classmethod
    def _open_vscode(cls) -> CommandResult:
        vscode = cls._find_vscode()
        if not vscode:
            return CommandResult(True, "VS Code was not found on this PC.")

        launch_cmd = [vscode]
        if Path(vscode).name.lower() == "code.cmd":
            launch_cmd = ["cmd", "/c", vscode]

        if cls._launch_command(launch_cmd):
            return CommandResult(True, "Opening VS Code.")
        return CommandResult(True, "VS Code could not be opened.")

    def route(self, text: str) -> CommandResult:
        lowered = text.lower().strip()

        if self._is_intro_prompt(lowered):
            return CommandResult(True, self.INTRO_RESPONSE)

        if any(k in lowered for k in ["open brave", "open browser", "open my browser", "launch brave", "launch browser"]):
            return self._open_brave()

        if any(k in lowered for k in ["open github", "open ghithub", "open github in browser", "open github browser"]):
            return self._open_url(self.GITHUB_URL, "GitHub")

        if any(k in lowered for k in ["open gmail", "open gmail in browser", "open gmail browser", "open my gmail"]):
            return self._open_url(self.GMAIL_URL, "Gmail")

        if "open youtube" in lowered:
            return self._open_url(self.YOUTUBE_URL, "YouTube")

        if any(k in lowered for k in ["open spotify", "launch spotify"]):
            return self._open_spotify()

        if any(k in lowered for k in ["open notepad", "launch notepad"]):
            return self._open_notepad()

        if any(k in lowered for k in ["open calculator", "open calc", "launch calculator", "launch calc"]):
            return self._open_calculator()

        if any(k in lowered for k in ["open vs code", "open vscode", "open visual studio code", "launch vs code", "launch vscode"]):
            return self._open_vscode()

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
