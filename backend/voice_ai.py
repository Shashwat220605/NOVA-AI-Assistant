import os
import re
from datetime import datetime

import numpy as np
import requests
import scipy.io.wavfile as wav
import sounddevice as sd
import whisper
import pyttsx3
from google import genai

from desktop_automation import (
    control_media,
    control_volume,
    create_folder,
    lock_computer,
    open_application,
    open_folder,
    open_url,
    take_screenshot,
    web_search,
)


# ============================================================
# SETTINGS
# ============================================================
SAMPLE_RATE = 16000
SILENCE_TIMEOUT = 5
AUDIO_FILE = "voice.wav"
MICROPHONE_DEVICE = 1
SPEECH_THRESHOLD = 300
BACKEND_URL = "http://127.0.0.1:8000"


def set_state(state):
    try:
        requests.post(f"{BACKEND_URL}/state/{state}", timeout=2)
    except requests.RequestException:
        pass


def handle_desktop_command(text):
    """Handle explicitly supported Windows actions.

    Commands run only after voice input. No arbitrary shell commands,
    continuous screen monitoring, OCR, browser drivers, or background
    automation services are used, keeping NOVA lightweight on mid-range PCs.
    """
    text = text.lower().strip()

    app_patterns = {
        "chrome": ["open chrome", "launch chrome", "start chrome", "open google chrome"],
        "vs code": ["open vs code", "launch vs code", "open visual studio code", "open vscode"],
        "discord": ["open discord", "launch discord", "start discord"],
        "spotify": ["open spotify", "launch spotify", "start spotify"],
        "calculator": ["open calculator", "open calc", "launch calculator"],
        "notepad": ["open notepad", "launch notepad"],
        "file explorer": ["open file explorer", "open explorer", "open my files"],
        "settings": ["open settings", "open windows settings"],
    }
    for app, phrases in app_patterns.items():
        if any(phrase in text for phrase in phrases):
            return open_application(app)

    folder_patterns = {
        "downloads": ["open downloads", "open my downloads", "show downloads"],
        "documents": ["open documents", "open my documents"],
        "desktop": ["open desktop", "show desktop folder"],
        "pictures": ["open pictures", "open photos"],
        "music": ["open music", "open my music"],
        "videos": ["open videos", "open my videos"],
    }
    for folder, phrases in folder_patterns.items():
        if any(phrase in text for phrase in phrases):
            return open_folder(folder)

    if any(p in text for p in ["take a screenshot", "take screenshot", "capture my screen", "screenshot"]):
        return take_screenshot()

    # Media and volume are on-demand only, so they have negligible idle cost.
    if any(p in text for p in ["play music", "resume music", "play media", "pause music", "pause media", "play pause"]):
        action = "pause" if "pause" in text and "play" not in text else "play"
        return control_media(action)
    if any(p in text for p in ["next song", "next track", "skip song", "skip track"]):
        return control_media("next")
    if any(p in text for p in ["previous song", "previous track", "go back song"]):
        return control_media("previous")
    if any(p in text for p in ["volume up", "increase volume", "turn volume up", "louder"]):
        return control_volume("up")
    if any(p in text for p in ["volume down", "decrease volume", "turn volume down", "quieter"]):
        return control_volume("down")
    if any(p in text for p in ["mute volume", "mute computer", "unmute volume", "unmute computer"]):
        return control_volume("mute")

    youtube_match = re.search(r"(?:search|find) youtube for (.+)", text)
    if youtube_match:
        return web_search(youtube_match.group(1), site="youtube")

    google_match = re.search(r"(?:search|google) for (.+)", text)
    if google_match:
        return web_search(google_match.group(1))

    url_match = re.search(r"(?:open|go to|visit)\s+((?:https?://)?(?:www\.)?[^\s]+\.[a-z]{2,}(?:/[^\s]*)?)", text)
    if url_match:
        return open_url(url_match.group(1))

    folder_match = re.search(r"(?:create|make) (?:a )?folder(?: called| named)? (.+)", text)
    if folder_match:
        return create_folder(folder_match.group(1))

    if any(p in text for p in ["lock my computer", "lock the computer", "lock my pc"]):
        return lock_computer()

    # Destructive power actions are intentionally not executed from voice alone.
    if any(p in text for p in ["shutdown computer", "shut down computer"]):
        return "Shutdown is available, but NOVA requires confirmation before doing that."
    if any(p in text for p in ["restart computer", "restart my computer"]):
        return "Restart is available, but NOVA requires confirmation before doing that."
    if any(p in text for p in ["put computer to sleep", "sleep computer"]):
        return "Sleep is available, but NOVA requires confirmation before doing that."

    return None


def handle_local_command(text):
    text = text.lower().strip()

    if any(p in text for p in ["what is your name", "what's your name", "who are you", "your name"]):
        return "My name is NOVA. I am your personal AI assistant."

    if any(p in text for p in ["what can you do", "what are your capabilities", "what do you do"]):
        return "I can answer questions, control supported computer tasks, open apps and folders, take screenshots, control media and volume, search the web, and control my visual interface."

    if text in {"hello", "hi", "hey", "hello nova", "hi nova", "hey nova"}:
        return "Hello. How can I help you?"

    if any(p in text for p in ["are you there", "are you online", "are you working"]):
        return "I'm online and ready."

    if any(p in text for p in ["what time is it", "tell me the time", "current time"]):
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."

    return None


print("Connecting to Gemini...")
client = genai.Client()
chat = client.chats.create(
    model="gemini-3.6-flash",
    config={
        "system_instruction": """
You are NOVA, a personal AI voice assistant.
Your name is NOVA.
Gemini is the AI model powering you. You are not Gemini.
If asked your name, say NOVA.
If asked who you are, say you are NOVA, their personal AI assistant.
If asked what powers you, explain that Google Gemini powers your AI responses.
Never introduce yourself as Gemini. Never claim to be human.
Be helpful, natural, and concise.
You are a desktop AI assistant.
"""
    },
)

print("Initializing voice system...")
tts = pyttsx3.init()
tts.setProperty("rate", 175)

print("\nLoading Whisper model...")
print("This may take a little while on CPU.\n")
model = whisper.load_model("base")
print("Whisper loaded.")

print("\n========================================")
print("             NOVA ONLINE")
print("========================================")
print("Microphone device:", MICROPHONE_DEVICE)
print("NOVA will shut down after 5 seconds without speech.")
print("Say 'stop nova' to shut down manually.")
print("========================================\n")

set_state("idle")

while True:
    set_state("listening")
    print("\n🎤 Listening...")

    try:
        audio = sd.rec(
            int(SILENCE_TIMEOUT * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            device=MICROPHONE_DEVICE,
        )
        sd.wait()
    except sd.PortAudioError as error:
        print("🎤 Microphone temporarily unavailable:", error)
        set_state("idle")
        continue
    except Exception as error:
        print("❌ Microphone error:", error)
        set_state("idle")
        continue

    audio_float = audio.astype(np.float32)
    rms = np.sqrt(np.mean(audio_float ** 2))
    print(f"Audio level: {rms:.0f}")

    if rms < SPEECH_THRESHOLD:
        set_state("speaking")
        print("NOVA: Goodbye.")
        try:
            tts.say("Goodbye.")
            tts.runAndWait()
        except Exception as error:
            print("TTS error:", error)
        set_state("idle")
        break

    try:
        wav.write(AUDIO_FILE, SAMPLE_RATE, audio)
    except Exception as error:
        print("❌ Could not save audio:", error)
        set_state("idle")
        continue

    print("\n🧠 Understanding...")
    set_state("thinking")

    try:
        result = model.transcribe(AUDIO_FILE)
        user_text = result["text"].strip()
    except Exception as error:
        print("❌ Whisper error:", error)
        set_state("idle")
        continue

    if not user_text:
        set_state("idle")
        continue

    print("\nYou:", user_text)

    if "stop nova" in user_text.lower():
        set_state("speaking")
        try:
            tts.say("Shutting down.")
            tts.runAndWait()
        except Exception as error:
            print("TTS error:", error)
        set_state("idle")
        break

    # Local/desktop actions run before Gemini. This avoids network requests
    # and extra model work for simple computer commands.
    ai_response = handle_local_command(user_text)
    if ai_response is None:
        ai_response = handle_desktop_command(user_text)

    if ai_response is None:
        print("🤖 NOVA is thinking...")
        try:
            response = chat.send_message(user_text)
            ai_response = response.text
        except Exception as error:
            print("❌ Gemini error:", error)
            ai_response = "Sorry, I couldn't connect to my AI brain."

    print("\nNOVA:")
    print(ai_response)

    set_state("speaking")
    try:
        tts.say(ai_response)
        tts.runAndWait()
    except Exception as error:
        print("❌ TTS error:", error)

    set_state("idle")
    print("\n----------------------------------------")
