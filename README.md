# NOVA - Personal AI Desktop Assistant

> A lightweight desktop AI assistant combining voice interaction,
> generative AI, speech recognition, text-to-speech, desktop automation,
> real-time system telemetry, and a custom 3D interface.

## Overview

NOVA is a personal AI desktop assistant built as a complete AI
application rather than a simple chatbot.

It combines a React + Three.js interface, a local FastAPI backend, and a
Python voice-processing pipeline. NOVA can listen to spoken commands,
convert speech to text with Whisper, send conversational requests to
Gemini, speak responses with text-to-speech, perform selected desktop
actions, and display lightweight system telemetry.

The project was designed to remain relatively lightweight for laptop
hardware by avoiding a continuously running local LLM.

## Features

-   🎤 Voice interaction
-   🧠 Gemini-powered conversational responses
-   👂 Whisper speech recognition
-   🔊 Local text-to-speech with `pyttsx3`
-   🖥️ Desktop automation
-   💠 Interactive Three.js 3D interface
-   📊 Lightweight system telemetry
-   ⚡ Local FastAPI backend
-   🚀 Automatic local server startup through `launcher.py`
-   📦 Windows executable packaging with PyInstaller
-   🔐 Environment-variable based API-key configuration

## Architecture

``` text
                    ┌─────────────────────┐
                    │        USER         │
                    │  Voice / UI Input   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React + Three.js  │
                    │     NOVA Interface  │
                    └──────────┬──────────┘
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │ FastAPI + Uvicorn   │
                    │   Local API Layer   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Voice Engine     │
                    │       Python        │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
          sounddevice       Whisper        Gemini
          Microphone       Speech-to-Text   AI Brain
                │              │              │
                └──────────────┴──────┬───────┘
                                      ▼
                                pyttsx3
                                Text-to-Speech
                                      │
                                      ▼
                                    USER
```

## Voice Pipeline

``` text
LISTEN
  ↓
Microphone recording
  ↓
Whisper transcription
  ↓
Command / conversation detection
  ↓
Gemini response when required
  ↓
Text-to-speech
  ↓
NOVA returns to READY
```

The interface reflects the main states:

``` text
READY → LISTENING → THINKING → SPEAKING → READY
```

## Technology Stack

  -----------------------------------------------------------------------
  Component               Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Frontend                React + Vite            User interface

  3D Interface            Three.js / React Three  NOVA core and visual
                          Fiber / Drei            effects

  Backend                 Python + FastAPI        Local API and control
                                                  layer

  Server                  Uvicorn                 Runs the FastAPI
                                                  application

  Speech-to-Text          Whisper                 Converts voice to text

  Audio Capture           sounddevice             Microphone recording

  AI                      Google Gemini           Natural-language
                                                  generation

  Text-to-Speech          pyttsx3                 Spoken responses

  Automation              Python / PyAutoGUI      Desktop actions

  Telemetry               psutil                  CPU, RAM and storage
                                                  information

  Packaging               PyInstaller             Windows executable
  -----------------------------------------------------------------------

## Project Structure

``` text
NOVA/
│
├── backend/
│   ├── server.py
│   ├── voice_ai.py
│   ├── api_test.py
│   ├── mic_test.py
│   └── voice_test.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── docs/
│   ├── NOVA_Project_Presentation.pdf
│   └── errors/
│
├── launcher.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the repository

``` bash
git clone https://github.com/YOUR_USERNAME/NOVA-AI-Assistant.git
cd NOVA-AI-Assistant
```

### 2. Create the Python environment

``` powershell
python -m venv backend\venv
```

Activate it:

``` powershell
.\backend\venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

``` powershell
pip install -r requirements.txt
```

### 4. Install frontend dependencies

``` powershell
cd frontend
npm install
```

### 5. Configure the Gemini API key

Create a `.env` file in the project root:

``` env
GEMINI_API_KEY=your_gemini_api_key_here
```

The `.env` file is intentionally excluded from Git.

A safe configuration template is provided as `.env.example`.

**Never commit a real API key to GitHub.**

### 6. Build the frontend

``` powershell
npm run build
```

### 7. Start NOVA

From the project root:

``` powershell
python launcher.py
```

The launcher starts the local FastAPI service and opens the NOVA
interface.

## System Telemetry

NOVA includes a lightweight telemetry panel displaying information such
as:

-   RAM usage and available memory
-   Storage usage and remaining space
-   CPU usage
-   CPU information
-   GPU information when available
-   Windows system information

Telemetry is sampled periodically instead of being calculated on every
3D animation frame. This keeps the interface responsive without
unnecessary background load.

## Performance Philosophy

NOVA was designed with laptop hardware limitations in mind.

The project avoids continuously running a local large language model and
instead uses an external AI service for conversational generation.

Performance considerations include:

-   Voice processing only when activated
-   Lightweight Three.js scene
-   Bounded particle effects
-   Periodic rather than per-frame telemetry updates
-   Local text-to-speech
-   FastAPI running as a local service

## Packaging

NOVA can be packaged for Windows using PyInstaller.

The packaged startup flow is:

``` text
NOVA.exe
   ↓
launcher.py
   ↓
FastAPI / Uvicorn
   ↓
NOVA Web Interface
   ↓
Voice Engine
```

Generated PyInstaller folders and executables are intentionally excluded
from the source repository through `.gitignore`.

A compiled executable can be distributed separately through GitHub
Releases.

## Problems & Solutions

During development, NOVA encountered several real-world integration
issues, including:

-   Python virtual-environment and PowerShell problems
-   Missing Python dependencies
-   Microphone and audio-device selection
-   Whisper and FFmpeg runtime requirements
-   WebRTC VAD native build issues
-   Gemini API configuration and service errors
-   PyAutoGUI / Pillow compatibility
-   FastAPI and Uvicorn startup problems
-   Port `8000` conflicts
-   PyInstaller missing files and Whisper assets
-   Executable path and resource handling
-   Windows Smart App Control blocking an unsigned executable
-   Browser-to-backend voice interaction issues

Detailed screenshots and solutions are documented in:

``` text
docs/errors/
```

## Documentation

The repository includes a presentation-style project document covering:

-   Project overview
-   Architecture
-   Technology stack
-   Voice pipeline
-   Frontend and backend design
-   System telemetry
-   Packaging
-   Development challenges
-   Security and performance
-   Presentation / viva flow
-   Future scope

See:

``` text
docs/NOVA_Project_Presentation.pdf
```

## Security

NOVA requires an AI API key for Gemini-based responses.

For security:

-   Store the key in `.env`
-   Never commit `.env`
-   Never hard-code API keys into source code
-   Use `.env.example` as the public configuration template
-   If a real key is exposed publicly, revoke it and generate a
    replacement

Desktop automation should also be restricted to explicitly supported
commands rather than allowing arbitrary model-generated shell commands.

## Future Improvements

NOVA is considered a complete portfolio project in its current form.
Possible future improvements include:

-   Lightweight wake-word activation
-   Activity and conversation history
-   More reactive 3D visualizations
-   Additional safe desktop commands
-   Signed Windows builds
-   Improved error recovery
-   More configurable AI providers

## Project Goal

The goal of NOVA was not simply to create another chatbot.

It was to build an end-to-end AI application where multiple technologies
work together:

``` text
INPUT
  ↓
SPEECH RECOGNITION
  ↓
AI INTERPRETATION
  ↓
ACTION / RESPONSE
  ↓
TEXT-TO-SPEECH
  ↓
VISUAL FEEDBACK
```

## Author

**Shashwat Ghadge**

B.Tech Computer Science & Engineering

Built as a personal AI/GenAI portfolio project.

------------------------------------------------------------------------

⭐ If you find the project interesting, consider giving the repository a
star.
