# AI Assistant

A basic desktop AI assistant with:
- Local LLM chat via `gemma2:9b-it` (Ollama-compatible localhost API)
- Speech-to-text input
- Picovoice wake word trigger
- Gesture control (`fist` play/pause, `pinch` next track, `thumb+middle pinch` exit app)
- Voice/text commands (`open youtube`, `power off`)
- Chat-focused Tkinter UI (background services auto-start)

## Project structure

- `assistant_app/core`: settings, LLM client, media keys, TTS
- `assistant_app/features/chat`: chatbot logic
- `assistant_app/features/voice`: speech-to-text listener
- `assistant_app/features/gesture`: webcam gesture detection
- `assistant_app/features/commands`: command routing and system actions
- `assistant_app/features/wake_word`: Picovoice wake word detection
- `assistant_app/ui`: desktop UI
- `config`: runtime configuration
- `scripts`: run helpers

## Setup (Windows)

1. Make sure Ollama (or compatible server) is running on `http://localhost:11434`.
2. Ensure your model is available, e.g. `gemma2:9b-it`.
3. In PowerShell:

```powershell
cd t:\CODE\ⲥⲭⲏⲙⲁ\luna
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1
```

## Notes

- STT currently uses `SpeechRecognition` default backend (`recognize_google`) for quick setup.
- Wake word uses Picovoice Porcupine (`pvporcupine` + `pvrecorder`).
- Add your Picovoice key in `config/assistant_config.json` under `wake_word.access_key`.
- Use `wake_word.keywords` for built-in words, or `wake_word.keyword_paths` for your custom `.ppn` file.
- UI is chat-only; wake word and gesture run in the background automatically.
- Shutdown command asks for confirmation in UI before execution.
- You can tweak model/settings in `config/assistant_config.json`.
- Close the gesture camera window with `q` when needed.
