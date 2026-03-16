# LUNA - AI Assistant

<img width="1536" height="1024" alt="LUNA AI Assistant Banner" src="https://github.com/user-attachments/assets/4271e0e0-0b7f-4996-a993-ff27283c1173" />

LUNA is a desktop AI assistant developed by **Joel Jacob**, a **III BSc Artificial Intelligence and Machine Learning student** at **Sree Narayana Guru College, Coimbatore**.

It is designed to make human-computer interaction smarter and more natural through **voice commands**, **speech-to-text interaction**, **wake word detection**, and **gesture-based media control**.

## Features

- Local LLM chat using `gemma2:9b-it` through an Ollama-compatible localhost API
- Speech-to-text input
- Picovoice wake word trigger
- Voice commands for opening apps and performing actions
- Gesture-based media control
- Chat-focused Tkinter UI
- Background services for wake word and gesture detection

## UI Reference Preview

Below is the reference image of the UI used in LUNA.

<img width="1920" height="864" alt="LUNA UI Reference" src="https://github.com/user-attachments/assets/a935145a-56b3-450f-a2e4-f98b239c49cd" />

## Gesture Reference Preview

Below is the reference image of the hand gestures used in LUNA for gesture-based media control.

<img width="1920" height="864" alt="LUNA Gesture Reference" src="https://github.com/user-attachments/assets/9cfc6476-e584-4ad1-a54c-625c3ed95336" />

## Demo Videos

### Voice Command Demo
https://github.com/user-attachments/assets/75de1a96-49e2-430b-a4fb-02e5b750c3e7

### Gesture Control Demo
https://github.com/user-attachments/assets/b8967cfa-203d-4795-9b13-6fe43e862852

## Gesture Controls

- **Fist** → Play / Pause
- **Pinch** → Next Track
- **Thumb + Middle Pinch** → Exit App

## Sample Voice Commands

- `open youtube`
- `open google`
- `open notepad`
- `queries and questions`

## Model Reference

LUNA uses local language models for chat and assistant responses. The primary model used is **gemma-2-9b-it**, and lighter alternatives such as **smollm2-1.7b-instruct** can also be configured depending on performance needs.

### Hugging Face Model Screenshot

`gemma-2-9b-it` model reference.

<img width="1898" height="931" alt="Image" src="https://github.com/user-attachments/assets/3b19af07-314a-426f-a0cf-ef6e31c3fe97" />


## LM Studi Developer Logs

Below is a screenshot of the developer logs showing LUNA running in the development environment.

<img width="1855" height="921" alt="Image" src="https://github.com/user-attachments/assets/97c0dd56-3820-41a3-b1f4-04e65f0ffa07" />

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
2. Ensure your model is available, for example `smollm2-1.7b-instruct` or `gemma-2-9b-it`
3. Open PowerShell and run:

```powershell
cd t:\CODE\ⲥⲭⲏⲙⲁ\luna
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1
