from __future__ import annotations

import threading

import speech_recognition as sr


class VoiceListener:
    def __init__(
        self,
        on_text,
        energy_threshold: int,
        pause_threshold: float,
        phrase_time_limit: int,
    ) -> None:
        self.on_text = on_text
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.phrase_time_limit = phrase_time_limit

        self._running = False
        self._thread: threading.Thread | None = None
        self._mic_lock = threading.Lock()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        try:
            while self._running:
                try:
                    text = self.listen_once(timeout=1, phrase_time_limit=self.phrase_time_limit)
                    if text:
                        self.on_text(text)
                except Exception as exc:
                    self.on_text(f"[Voice error: {exc}]")
        finally:
            self._running = False

    def listen_once(self, timeout: int = 5, phrase_time_limit: int | None = None) -> str | None:
        limit = phrase_time_limit if phrase_time_limit is not None else self.phrase_time_limit
        with self._mic_lock:
            with sr.Microphone() as source:
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=limit)
                    text = self.recognizer.recognize_google(audio).strip()
                    return text or None
                except sr.WaitTimeoutError:
                    return None
                except sr.UnknownValueError:
                    return None
