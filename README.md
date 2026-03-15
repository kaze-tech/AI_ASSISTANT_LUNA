# LUNA - AI Assistant

LUNA is a desktop AI assistant developed by **Joel Jacob**, a **II BSc Artificial Intelligence and Machine Learning student** at **Sree Narayana Guru College, Coimbatore**.

It is designed to make human-computer interaction smarter and more natural through **voice commands**, **speech-to-text interaction**, **wake word detection**, and **gesture-based media control**.

## Features

- Local LLM chat using `gemma2:9b-it` through an Ollama-compatible localhost API
- Speech-to-text input
- Picovoice wake word trigger
- Voice commands for opening apps and performing actions
- Gesture-based media control
- Chat-focused Tkinter UI
- Background services for wake word and gesture detection

## Demo Videos

### Voice Command Demo
Add your demo video link here:  
[Voice Command Demo](PASTE_YOUR_VIDEO_LINK_HERE)

### Gesture Control Demo
[![Gesture Control Demo](https://img.youtube.com/vi/FsxVMy7Yszo/0.jpg)](https://youtu.be/FsxVMy7Yszo)

## Gesture Controls

- **Fist** → Play / Pause
- **Pinch** → Next Track
- **Thumb + Middle Pinch** → Exit App

## Sample Voice Commands

- `open youtube`
- `open google`
- `open notepad`
- `power off`

## Project Structure

- `assistant_app/core` — settings, LLM client, media keys, TTS
- `assistant_app/features/chat` — chatbot logic
- `assistant_app/features/voice` — speech-to-text listener
- `assistant_app/features/gesture` — webcam gesture detection
- `assistant_app/features/commands` — command routing and system actions
- `assistant_app/features/wake_word` — Picovoice wake word detection
- `assistant_app/ui` — desktop UI
- `config` — runtime configuration
- `scripts` — run helpers

## Setup (Windows)

1. Make sure Ollama or a compatible server is running on `http://localhost:11434`
2. Ensure your model is available, for example `gemma2:9b-it`
3. Open PowerShell and run:

```powershell
cd t:\CODE\ⲥⲭⲏⲙⲁ\luna
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1
