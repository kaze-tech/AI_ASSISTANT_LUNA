from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    llm_base_url: str
    llm_generate_path: str
    llm_model: str
    llm_api_type: str
    llm_max_tokens: int
    llm_temperature: float
    assistant_name: str
    system_prompt: str
    speak_replies: bool
    voice_energy_threshold: int
    voice_pause_threshold: float
    voice_phrase_time_limit: int
    gesture_camera_index: int
    gesture_cooldown_seconds: float
    gesture_show_camera_window: bool
    gesture_hold_frames: int
    gesture_release_frames: int
    gesture_finger_margin: float
    gesture_pinch_distance_threshold: float
    gesture_pinch_hold_frames: int
    gesture_pinch_cooldown_seconds: float
    wake_word_enabled_by_default: bool
    wake_word_access_key: str
    wake_word_keywords: list[str]
    wake_word_keyword_paths: list[str]
    wake_word_sensitivity: float
    wake_word_device_index: int
    wake_word_listen_timeout: int
    wake_word_phrase_time_limit: int


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "assistant_config.json"


def load_settings(path: Path | None = None) -> Settings:
    config_path = path or DEFAULT_CONFIG_PATH
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    wake = payload.get("wake_word", {})

    return Settings(
        llm_base_url=payload["llm"]["base_url"],
        llm_generate_path=payload["llm"]["generate_path"],
        llm_model=payload["llm"]["model"],
        llm_api_type=payload["llm"].get("api_type", "auto"),
        llm_max_tokens=int(payload["llm"].get("max_tokens", 180)),
        llm_temperature=float(payload["llm"].get("temperature", 0.6)),
        assistant_name=payload["assistant"]["name"],
        system_prompt=payload["assistant"]["system_prompt"],
        speak_replies=payload["assistant"].get("speak_replies", False),
        voice_energy_threshold=payload["voice"]["energy_threshold"],
        voice_pause_threshold=payload["voice"]["pause_threshold"],
        voice_phrase_time_limit=payload["voice"]["phrase_time_limit"],
        gesture_camera_index=payload["gesture"]["camera_index"],
        gesture_cooldown_seconds=payload["gesture"]["cooldown_seconds"],
        gesture_show_camera_window=payload["gesture"]["show_camera_window"],
        gesture_hold_frames=int(payload["gesture"].get("hold_frames", 4)),
        gesture_release_frames=int(payload["gesture"].get("release_frames", 4)),
        gesture_finger_margin=float(payload["gesture"].get("finger_margin", 0.02)),
        gesture_pinch_distance_threshold=float(payload["gesture"].get("pinch_distance_threshold", 0.045)),
        gesture_pinch_hold_frames=int(payload["gesture"].get("pinch_hold_frames", 3)),
        gesture_pinch_cooldown_seconds=float(payload["gesture"].get("pinch_cooldown_seconds", 1.0)),
        wake_word_enabled_by_default=wake.get("enabled_by_default", False),
        wake_word_access_key=wake.get("access_key", ""),
        wake_word_keywords=wake.get("keywords", ["computer"]),
        wake_word_keyword_paths=wake.get("keyword_paths", []),
        wake_word_sensitivity=float(wake.get("sensitivity", 0.6)),
        wake_word_device_index=int(wake.get("device_index", -1)),
        wake_word_listen_timeout=int(wake.get("listen_timeout", 5)),
        wake_word_phrase_time_limit=int(wake.get("phrase_time_limit", 6)),
    )
