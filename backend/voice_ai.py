from datetime import datetime

import numpy as np
import requests
import scipy.io.wavfile as wav
import sounddevice as sd
import whisper
import pyttsx3
from google import genai

from command_engine import Intent, detect_intent, detect_multi_intents
from confirmation_store import set_pending
from desktop_automation import (
    control_media, control_volume, control_window, create_folder, get_active_window,
    lock_computer, open_application, open_folder, open_site, open_url, take_screenshot, web_search,
)

SAMPLE_RATE = 16000
MAX_RECORD_SECONDS = 5
CHUNK_SECONDS = 0.25
START_TIMEOUT_SECONDS = 2.5
END_SILENCE_SECONDS = 0.75
AUDIO_FILE = "voice.wav"
MICROPHONE_DEVICE = 1
SPEECH_THRESHOLD = 300
BACKEND_URL = "http://127.0.0.1:8000"


def set_state(state, message=None, confirmation=None):
    payload = {}
    if message is not None: payload["message"] = message
    if confirmation is not None: payload["confirmation"] = confirmation
    try: requests.post(f"{BACKEND_URL}/state/{state}", json=payload, timeout=2)
    except requests.RequestException: pass


def record_speech():
    chunks, heard_speech, silent_chunks = [], False, 0
    max_chunks = int(MAX_RECORD_SECONDS / CHUNK_SECONDS)
    start_timeout_chunks = int(START_TIMEOUT_SECONDS / CHUNK_SECONDS)
    end_silence_chunks = int(END_SILENCE_SECONDS / CHUNK_SECONDS)
    for index in range(max_chunks):
        audio = sd.rec(int(CHUNK_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16", device=MICROPHONE_DEVICE)
        sd.wait(); chunks.append(audio)
        rms = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
        if rms >= SPEECH_THRESHOLD:
            heard_speech, silent_chunks = True, 0
        elif heard_speech:
            silent_chunks += 1
            if silent_chunks >= end_silence_chunks: break
        elif index + 1 >= start_timeout_chunks: break
    if not heard_speech: return None
    trimmed = chunks[:len(chunks) - silent_chunks] if silent_chunks else chunks
    return np.concatenate(trimmed, axis=0)


def handle_local_command(text):
    intent = detect_intent(text)
    if intent is None: return None
    responses = {
        "greeting": "Hello. How can I help you?", "identity": "My name is NOVA. I am your personal AI assistant.",
        "capabilities": "I can answer questions, control supported computer tasks, manage windows, open apps and folders, identify the active window, take screenshots, control media and volume, and open or search websites.",
        "status": "I'm online and ready.", "time": f"The current time is {datetime.now().strftime('%I:%M %p')}.",
    }
    return responses.get(intent.name)


def request_confirmation(intent: Intent) -> str:
    if intent.name == "power":
        labels = {"shutdown":"Shut down the computer", "restart":"Restart the computer", "sleep":"Put the computer to sleep"}
        label = labels.get(intent.argument, intent.argument.title()); set_pending("power", intent.argument, label)
    elif intent.name == "create_folder":
        label = f"Create folder '{intent.argument}'"; set_pending("create_folder", intent.argument, label)
    elif intent.name == "window" and intent.argument == "close":
        label = "Close the active window"; set_pending("window_close", "", label)
    else: return "I can't confirm that action."
    set_state("confirmation", f"Confirmation required: {label}.", {"label": label, "action": intent.name, "argument": intent.argument})
    return f"Please confirm: {label}."


def execute_intent(intent: Intent) -> str | None:
    if intent.requires_confirmation: return request_confirmation(intent)
    actions = {
        "open_app": lambda: open_application(intent.argument), "open_folder": lambda: open_folder(intent.argument),
        "active_window": get_active_window, "screenshot": take_screenshot, "lock": lock_computer,
        "open_site": lambda: open_site(intent.argument), "open_url": lambda: open_url(intent.argument),
        "web_search": lambda: web_search(intent.argument), "youtube_search": lambda: web_search(intent.argument, site="youtube"),
        "create_folder": lambda: create_folder(intent.argument), "media": lambda: control_media(intent.argument),
        "volume": lambda: control_volume(intent.argument), "window": lambda: control_window(intent.argument),
    }
    action = actions.get(intent.name)
    if action is None: return None
    set_state("executing", "Executing desktop action.")
    try:
        result = action(); set_state("success", result); return result
    except Exception as error:
        print("Desktop action error:", error); set_state("error", "Desktop action failed."); return "I couldn't complete that action."


def handle_desktop_command(text):
    intents = detect_multi_intents(text)
    if intents:
        results = []
        for index, intent in enumerate(intents, 1):
            result = execute_intent(intent)
            if result: results.append(f"Step {index}: {result}")
            if intent.requires_confirmation: break
        return " ".join(results) if results else None
    intent = detect_intent(text)
    if intent is None or intent.name in {"stop", "greeting", "identity", "capabilities", "status", "time"}: return None
    return execute_intent(intent)


print("Connecting to Gemini...")
client = genai.Client()
chat = client.chats.create(model="gemini-3.6-flash", config={"system_instruction": "You are NOVA, a personal AI voice assistant. Your name is NOVA. Gemini is the AI model powering you. Never introduce yourself as Gemini. Be helpful, natural, concise, and desktop-assistant focused."})
tts = pyttsx3.init(); tts.setProperty("rate", 175)
print("\nLoading Whisper model...\n")
model = whisper.load_model("base")
print("Whisper loaded.")
print("\nNOVA ONLINE | Voice capture: up to 5 seconds, silence-aware")
set_state("idle")

while True:
    set_state("listening"); print("\n🎤 Listening...")
    try: audio = record_speech()
    except sd.PortAudioError as error:
        print("🎤 Microphone temporarily unavailable:", error); set_state("idle"); continue
    except Exception as error:
        print("❌ Microphone error:", error); set_state("idle"); continue
    if audio is None: print("No speech detected."); set_state("idle"); continue
    try: wav.write(AUDIO_FILE, SAMPLE_RATE, audio)
    except Exception as error: print("❌ Could not save audio:", error); set_state("idle"); continue

    print("\n🧠 Understanding..."); set_state("thinking")
    try: user_text = model.transcribe(AUDIO_FILE)["text"].strip()
    except Exception as error: print("❌ Whisper error:", error); set_state("idle"); continue
    if not user_text: set_state("idle"); continue
    print("\nYou:", user_text)
    intent = detect_intent(user_text)
    if intent and intent.name == "stop":
        set_state("speaking"); tts.say("Shutting down."); tts.runAndWait(); set_state("idle"); break

    ai_response = handle_local_command(user_text)
    if ai_response is None: ai_response = handle_desktop_command(user_text)
    if ai_response is None:
        print("🤖 NOVA is thinking...")
        try: ai_response = chat.send_message(user_text).text
        except Exception as error: print("❌ Gemini error:", error); ai_response = "Sorry, I couldn't connect to my AI brain."

    print("\nNOVA:\n", ai_response)
    protected = bool(intent and intent.requires_confirmation)
    if not protected: set_state("speaking")
    try: tts.say(ai_response); tts.runAndWait()
    except Exception as error: print("❌ TTS error:", error)
    if not protected: set_state("idle")
