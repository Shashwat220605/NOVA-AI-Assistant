from datetime import datetime

import numpy as np
import requests
import scipy.io.wavfile as wav
import sounddevice as sd
import whisper
import pyttsx3
from google import genai

from command_engine import Intent, detect_intent
from confirmation_store import set_pending
from desktop_automation import (
    control_media, control_volume, create_folder, get_active_window,
    lock_computer, open_application, open_folder, open_site, open_url,
    take_screenshot, web_search,
)

SAMPLE_RATE = 16000
SILENCE_TIMEOUT = 5
AUDIO_FILE = "voice.wav"
MICROPHONE_DEVICE = 1
SPEECH_THRESHOLD = 300
BACKEND_URL = "http://127.0.0.1:8000"


def set_state(state, message=None, confirmation=None):
    payload = {}
    if message is not None:
        payload["message"] = message
    if confirmation is not None:
        payload["confirmation"] = confirmation
    try:
        requests.post(f"{BACKEND_URL}/state/{state}", json=payload, timeout=2)
    except requests.RequestException:
        pass


def handle_local_command(text):
    intent = detect_intent(text)
    if intent is None:
        return None
    responses = {
        "greeting": "Hello. How can I help you?",
        "identity": "My name is NOVA. I am your personal AI assistant.",
        "capabilities": "I can answer questions, control supported computer tasks, open apps and folders, identify the active window, take screenshots, control media and volume, and open or search websites.",
        "status": "I'm online and ready.",
        "time": f"The current time is {datetime.now().strftime('%I:%M %p')}.",
    }
    return responses.get(intent.name)


def request_confirmation(intent: Intent) -> str:
    if intent.name == "power":
        labels = {"shutdown": "Shut down the computer", "restart": "Restart the computer", "sleep": "Put the computer to sleep"}
        label = labels.get(intent.argument, intent.argument.title())
        set_pending("power", intent.argument, label)
    elif intent.name == "create_folder":
        label = f"Create folder '{intent.argument}'"
        set_pending("create_folder", intent.argument, label)
    else:
        return "I can't confirm that action."
    confirmation = {"label": label, "action": intent.name, "argument": intent.argument}
    set_state("confirmation", f"Confirmation required: {label}.", confirmation)
    return f"Please confirm: {label}."


def execute_intent(intent: Intent) -> str | None:
    if intent.requires_confirmation:
        return request_confirmation(intent)

    actions = {
        "open_app": lambda: open_application(intent.argument),
        "open_folder": lambda: open_folder(intent.argument),
        "active_window": get_active_window,
        "screenshot": take_screenshot,
        "lock": lock_computer,
        "open_site": lambda: open_site(intent.argument),
        "open_url": lambda: open_url(intent.argument),
        "web_search": lambda: web_search(intent.argument),
        "youtube_search": lambda: web_search(intent.argument, site="youtube"),
        "create_folder": lambda: create_folder(intent.argument),
        "media": lambda: control_media(intent.argument),
        "volume": lambda: control_volume(intent.argument),
    }
    action = actions.get(intent.name)
    if action is None:
        return None
    set_state("executing", "Executing desktop action.")
    try:
        result = action()
        set_state("success", result)
        return result
    except Exception as error:
        print("Desktop action error:", error)
        set_state("error", "Desktop action failed.")
        return "I couldn't complete that action."


def handle_desktop_command(text):
    intent = detect_intent(text)
    if intent is None:
        return None
    if intent.name in {"stop", "greeting", "identity", "capabilities", "status", "time"}:
        return None
    return execute_intent(intent)


print("Connecting to Gemini...")
client = genai.Client()
chat = client.chats.create(
    model="gemini-3.6-flash",
    config={"system_instruction": """
You are NOVA, a personal AI voice assistant.
Your name is NOVA.
Gemini is the AI model powering you. You are not Gemini.
If asked your name, say NOVA. If asked who you are, say you are NOVA, their personal AI assistant.
If asked what powers you, explain that Google Gemini powers your AI responses.
Never introduce yourself as Gemini. Never claim to be human.
Be helpful, natural, and concise. You are a desktop AI assistant.
"""},
)

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
        audio = sd.rec(int(SILENCE_TIMEOUT * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16", device=MICROPHONE_DEVICE)
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

    intent = detect_intent(user_text)
    if intent and intent.name == "stop":
        set_state("speaking")
        try:
            tts.say("Shutting down.")
            tts.runAndWait()
        except Exception as error:
            print("TTS error:", error)
        set_state("idle")
        break

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
    protected = bool(intent and intent.requires_confirmation)
    if not protected:
        set_state("speaking")
    try:
        tts.say(ai_response)
        tts.runAndWait()
    except Exception as error:
        print("❌ TTS error:", error)
    if not protected:
        set_state("idle")
    print("\n----------------------------------------")
