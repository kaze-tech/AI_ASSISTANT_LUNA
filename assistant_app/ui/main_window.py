from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from assistant_app.core.llm_client import LLMClient
from assistant_app.core.media_keys import get_now_playing_title, press_media_next_track, press_media_play_pause
from assistant_app.core.settings import load_settings
from assistant_app.core.tts_engine import TTSEngine
from assistant_app.features.chat.chat_manager import ChatManager
from assistant_app.features.commands.command_router import CommandRouter
from assistant_app.features.gesture.gesture_controller import GestureController
from assistant_app.features.voice.voice_listener import VoiceListener
from assistant_app.features.wake_word.wake_word_listener import WakeWordListener


class AssistantUI:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.colors = {
            "bg": "#09090b",
            "panel": "#111318",
            "panel_alt": "#171a21",
            "text": "#f3f4f6",
            "muted": "#9ca3af",
            "accent": "#22d3ee",
            "accent_hover": "#06b6d4",
            "line": "#232833",
            "user": "#38bdf8",
            "assistant": "#a78bfa",
            "system": "#f59e0b",
            "voice": "#10b981",
            "gesture": "#fb7185",
        }

        llm = LLMClient(
            base_url=self.settings.llm_base_url,
            generate_path=self.settings.llm_generate_path,
            model=self.settings.llm_model,
            api_type=self.settings.llm_api_type,
            max_tokens=self.settings.llm_max_tokens,
            temperature=self.settings.llm_temperature,
        )

        self.chat = ChatManager(llm, self.settings.system_prompt)
        self.commands = CommandRouter()
        self.tts = TTSEngine()

        self.root = tk.Tk()
        self.root.title(f"{self.settings.assistant_name} Chat")
        self.root.geometry("920x660")
        self.root.configure(bg=self.colors["bg"])

        container = tk.Frame(self.root, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        card = tk.Frame(
            container,
            bg=self.colors["panel"],
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            highlightcolor=self.colors["line"],
            padx=12,
            pady=12,
        )
        card.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            card,
            text=f"{self.settings.assistant_name} Chat",
            font=("Segoe UI Semibold", 18),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            anchor="w",
        )
        title.pack(fill=tk.X, pady=(0, 6))
        media_header = tk.Frame(
            card,
            bg=self.colors["panel_alt"],
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            highlightcolor=self.colors["line"],
            padx=10,
            pady=6,
        )
        media_header.pack(fill=tk.X, pady=(0, 10))
        self.media_icon_var = tk.StringVar(value="\u23EF")
        self.now_playing_var = tk.StringVar(value="Made by Joel")
        self.media_state_is_playing = False
        self.media_icon_label = tk.Label(
            media_header,
            textvariable=self.media_icon_var,
            font=("Segoe UI Symbol", 20),
            bg=self.colors["panel_alt"],
            fg=self.colors["accent"],
            anchor="w",
        )
        self.media_icon_label.pack(side=tk.LEFT)

        self.media_title_label = tk.Label(
            media_header,
            textvariable=self.now_playing_var,
            font=("Segoe UI", 10),
            bg=self.colors["panel_alt"],
            fg=self.colors["text"],
            anchor="w",
        )
        self.media_title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        self.status_var = tk.StringVar(value="Starting background services...")
        status = tk.Label(
            card,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg=self.colors["panel_alt"],
            fg=self.colors["muted"],
            anchor="w",
            padx=10,
            pady=6,
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            highlightcolor=self.colors["line"],
        )
        status.pack(fill=tk.X, pady=(0, 8))

        self.chat_log = ScrolledText(
            card,
            wrap=tk.WORD,
            height=24,
            state=tk.DISABLED,
            bg="#0c0f14",
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            font=("Segoe UI", 11),
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            highlightcolor=self.colors["accent"],
            padx=10,
            pady=10,
        )
        self.chat_log.pack(fill=tk.BOTH, expand=True)
        self.chat_log.tag_config("user", foreground=self.colors["user"])
        self.chat_log.tag_config("assistant", foreground=self.colors["assistant"])
        self.chat_log.tag_config("system", foreground=self.colors["system"])
        self.chat_log.tag_config("voice", foreground=self.colors["voice"])
        self.chat_log.tag_config("gesture", foreground=self.colors["gesture"])
        self.chat_log.tag_config("body", foreground=self.colors["text"])

        input_row = tk.Frame(card, bg=self.colors["panel"])
        input_row.pack(fill=tk.X, pady=(10, 0))

        self.entry = tk.Entry(
            input_row,
            font=("Segoe UI", 11),
            bg="#0c0f14",
            fg=self.colors["text"],
            relief=tk.SOLID,
            bd=1,
            insertbackground=self.colors["text"],
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            highlightcolor=self.colors["accent"],
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_send)

        send_btn = tk.Button(
            input_row,
            text="Send",
            command=self._on_send,
            font=("Segoe UI Semibold", 10),
            bg=self.colors["accent"],
            fg="#071014",
            activebackground=self.colors["accent_hover"],
            activeforeground="#071014",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            bd=0,
            cursor="hand2",
        )
        send_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.voice_listener = VoiceListener(
            on_text=self._on_voice_text,
            energy_threshold=self.settings.voice_energy_threshold,
            pause_threshold=self.settings.voice_pause_threshold,
            phrase_time_limit=self.settings.voice_phrase_time_limit,
        )

        self.gesture = GestureController(
            on_fist=self._on_fist,
            on_pinch=self._on_pinch,
            on_middle_pinch=self._on_middle_pinch,
            on_error=self._on_gesture_error,
            camera_index=self.settings.gesture_camera_index,
            cooldown_seconds=self.settings.gesture_cooldown_seconds,
            show_camera_window=self.settings.gesture_show_camera_window,
            hold_frames=self.settings.gesture_hold_frames,
            release_frames=self.settings.gesture_release_frames,
            finger_margin=self.settings.gesture_finger_margin,
            pinch_distance_threshold=self.settings.gesture_pinch_distance_threshold,
            pinch_hold_frames=self.settings.gesture_pinch_hold_frames,
            pinch_cooldown_seconds=self.settings.gesture_pinch_cooldown_seconds,
        )

        self.wake_word = WakeWordListener(
            access_key=self.settings.wake_word_access_key,
            keywords=self.settings.wake_word_keywords,
            keyword_paths=self.settings.wake_word_keyword_paths,
            sensitivity=self.settings.wake_word_sensitivity,
            device_index=self.settings.wake_word_device_index,
            on_detect=self._on_wake_word,
            on_error=self._on_wake_word_error,
        )

        self.gesture_running = False
        self.wake_word_running = False
        self._services_should_run = True
        self._wake_capture_running = False
        self._media_poll_job = None
        self._closing = False

        self._append("system", f"Connected to model: {self.settings.llm_model} at {self.settings.llm_base_url}")
        self._refresh_now_playing()
        self._start_background_services()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _append(self, speaker: str, text: str) -> None:
        self.chat_log.configure(state=tk.NORMAL)
        tag = speaker if speaker in {"user", "assistant", "system", "voice", "gesture"} else "body"
        label = speaker.upper()
        self.chat_log.insert(tk.END, f"{label}\n", tag)
        self.chat_log.insert(tk.END, f"{text}\n\n", "body")
        self.chat_log.see(tk.END)
        self.chat_log.configure(state=tk.DISABLED)

    def _on_send(self, _event=None) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._append("you", text)
        threading.Thread(target=self._process_user_text, args=(text,), daemon=True).start()

    def _on_voice_text(self, text: str) -> None:
        self.root.after(0, lambda: self._append("voice", text))
        threading.Thread(target=self._process_user_text, args=(text,), daemon=True).start()

    def _on_fist(self) -> None:
        press_media_play_pause()
        self.media_state_is_playing = not self.media_state_is_playing
        icon = "\u23F8" if self.media_state_is_playing else "\u25B6"
        self.root.after(0, lambda: self.media_icon_var.set(icon))
        self.root.after(0, lambda: self.now_playing_var.set("Gesture: Fist (play/pause)"))
        self.root.after(700, self._refresh_now_playing_once)

    def _on_pinch(self) -> None:
        press_media_next_track()
        self.root.after(0, lambda: self.now_playing_var.set("Gesture: Pinch (next track)"))
        self.root.after(700, self._refresh_now_playing_once)

    def _on_middle_pinch(self) -> None:
        self.root.after(0, lambda: self.now_playing_var.set("Gesture: Thumb+Middle (shutdown)"))
        self.root.after(150, self._on_close)

    def _refresh_now_playing_once(self) -> None:
        title = get_now_playing_title()
        display_title = title if title else "Made by Joel"
        self.now_playing_var.set(display_title)

    def _refresh_now_playing(self) -> None:
        self._refresh_now_playing_once()
        if self._services_should_run:
            self._media_poll_job = self.root.after(3000, self._refresh_now_playing)

    def _on_wake_word(self) -> None:
        if self._wake_capture_running:
            return
        self.root.after(0, lambda: self._append("system", "Wake word detected. Listening..."))
        self._wake_capture_running = True
        threading.Thread(target=self._capture_wake_command, daemon=True).start()

    def _on_gesture_error(self, error_text: str) -> None:
        self.root.after(0, lambda: self._append("system", f"Gesture error: {error_text}"))
        self.root.after(0, lambda: self.status_var.set("Gesture error. Install compatible mediapipe."))
        self.gesture_running = False

    def _on_wake_word_error(self, error_text: str) -> None:
        self.root.after(0, lambda: self._append("system", f"Wake word error: {error_text}"))
        self.root.after(0, lambda: self.status_var.set("Wake word error. Check key/keyword path."))
        self.wake_word_running = False

    def _capture_wake_command(self) -> None:
        try:
            # Free the input device used by Porcupine before STT capture.
            self.wake_word.stop()
            time.sleep(0.25)
            text = self.voice_listener.listen_once(
                timeout=self.settings.wake_word_listen_timeout,
                phrase_time_limit=self.settings.wake_word_phrase_time_limit,
            )
            if not text:
                self.root.after(0, lambda: self._append("system", "No speech captured after wake word."))
                return
            self.root.after(0, lambda: self._append("voice", text))
            threading.Thread(target=self._process_user_text, args=(text,), daemon=True).start()
        finally:
            if self._services_should_run and self.wake_word_running:
                self.wake_word.start()
            self._wake_capture_running = False

    def _process_user_text(self, text: str) -> None:
        command = self.commands.route(text)
        if command.handled:
            self.root.after(0, lambda: self._append("assistant", command.message))
            if command.needs_confirmation and command.confirm_action:
                self.root.after(0, lambda: self._confirm_and_execute(command.confirm_action))
            return

        try:
            reply = self.chat.ask(text)
        except Exception as exc:
            reply = f"LLM error: {exc}"

        self.root.after(0, lambda: self._append("assistant", reply))
        if self.settings.speak_replies:
            self.tts.speak(reply)

    def _confirm_and_execute(self, action: str) -> None:
        ok = messagebox.askyesno("Confirm", "Do you want to power off the PC now?")
        if not ok:
            self._append("assistant", "Power off cancelled.")
            return
        msg = self.commands.run_confirmed_action(action)
        self._append("assistant", msg)

    def _start_background_services(self) -> None:
        self.gesture.start()
        self.gesture_running = True
        self._append("system", "Gesture detection active (fist = play/pause, pinch = next track, thumb+middle pinch = exit).")

        if self.settings.wake_word_access_key.strip():
            self.wake_word_running = True
            self.wake_word.start()
            self._append("system", "Wake word active. Say your keyword, then speak command.")
            self.status_var.set("Ready: chat + wake word + gesture")
        else:
            self.status_var.set("Ready: chat + gesture (wake word key missing)")
            self._append("system", "Wake word disabled: add Picovoice key in config.")

    def _on_close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self._services_should_run = False
        if self._media_poll_job is not None:
            self.root.after_cancel(self._media_poll_job)
            self._media_poll_job = None
        self.gesture.stop()
        self.wake_word.stop()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()

