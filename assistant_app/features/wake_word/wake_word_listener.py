from __future__ import annotations

import threading

import pvporcupine
from pvrecorder import PvRecorder


class WakeWordListener:
    def __init__(
        self,
        access_key: str,
        on_detect,
        on_error,
        keywords: list[str] | None = None,
        keyword_paths: list[str] | None = None,
        sensitivity: float = 0.6,
        device_index: int = -1,
    ) -> None:
        self.access_key = access_key
        self.keywords = keywords or ["computer"]
        self.keyword_paths = keyword_paths or []
        self.sensitivity = sensitivity
        self.device_index = device_index
        self.on_detect = on_detect
        self.on_error = on_error

        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        porcupine = None
        recorder = None
        try:
            if not self.access_key.strip():
                raise RuntimeError("Picovoice access key missing in config.")

            sensitivities = [self.sensitivity] * max(len(self.keyword_paths), len(self.keywords))
            create_args = {
                "access_key": self.access_key,
                "sensitivities": sensitivities,
            }
            if self.keyword_paths:
                create_args["keyword_paths"] = self.keyword_paths
            else:
                create_args["keywords"] = self.keywords

            porcupine = pvporcupine.create(**create_args)
            recorder = PvRecorder(device_index=self.device_index, frame_length=porcupine.frame_length)
            recorder.start()

            while self._running:
                pcm = recorder.read()
                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    self.on_detect()
        except Exception as exc:
            self.on_error(str(exc))
        finally:
            if recorder is not None:
                recorder.stop()
                recorder.delete()
            if porcupine is not None:
                porcupine.delete()
            self._running = False
