import os
import subprocess
from datetime import datetime

import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import whisper
import pyttsx3
import requests

from google import genai


# ============================================================
# SETTINGS
# ============================================================

SAMPLE_RATE = 16000

# NOVA waits this long for speech
SILENCE_TIMEOUT = 5

AUDIO_FILE = "voice.wav"

# Your working microphone
MICROPHONE_DEVICE = 1

# Audio level considered speech
# Lower = more sensitive
SPEECH_THRESHOLD = 300

# NOVA backend
BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# STATE
# ============================================================

def set_state(state):

    try:

        requests.post(
            f"{BACKEND_URL}/state/{state}",
            timeout=2
        )

    except requests.RequestException:

        pass


# ============================================================
# LOCAL COMMANDS
# ============================================================

def handle_local_command(text):

    text = text.lower().strip()

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "what is your name",
        "what's your name",
        "who are you",
        "your name"
    ]):

        return (
            "My name is NOVA. "
            "I am your personal AI assistant."
        )


    # --------------------------------------------------------
    # CAPABILITIES
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "what can you do",
        "what are your capabilities",
        "what do you do"
    ]):

        return (
            "I can answer questions, open applications, "
            "perform some computer tasks, and control "
            "my visual interface."
        )


    # --------------------------------------------------------
    # GREETINGS
    # --------------------------------------------------------

    if text in [
        "hello",
        "hi",
        "hey",
        "hello nova",
        "hi nova",
        "hey nova"
    ]:

        return "Hello. How can I help you?"


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "are you there",
        "are you online",
        "are you working"
    ]):

        return "I'm online and ready."


    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "what time is it",
        "tell me the time",
        "current time"
    ]):

        current_time = datetime.now().strftime(
            "%I:%M %p"
        )

        return f"The current time is {current_time}."


    # --------------------------------------------------------
    # OPEN VS CODE
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "open vs code",
        "open visual studio code",
        "launch vs code"
    ]):

        try:

            subprocess.Popen(["code"])

            return "Opening Visual Studio Code."

        except Exception:

            return "I couldn't open Visual Studio Code."


    # --------------------------------------------------------
    # OPEN CHROME
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "open chrome",
        "launch chrome",
        "start chrome"
    ]):

        chrome_paths = [

            r"C:\Program Files\Google\Chrome\Application\chrome.exe",

            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        ]

        for path in chrome_paths:

            if os.path.exists(path):

                subprocess.Popen([path])

                return "Opening Google Chrome."

        return "I couldn't find Google Chrome."


    # --------------------------------------------------------
    # OPEN DISCORD
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "open discord",
        "launch discord",
        "start discord"
    ]):

        try:

            discord_update = os.path.expandvars(
                r"%LOCALAPPDATA%\Discord\Update.exe"
            )

            if os.path.exists(discord_update):

                subprocess.Popen(
                    [
                        discord_update,
                        "--processStart",
                        "Discord.exe"
                    ]
                )

                return "Opening Discord."


            os.startfile("discord://")

            return "Opening Discord."

        except Exception as error:

            print("Discord error:", error)

            return "I couldn't open Discord."


    # --------------------------------------------------------
    # FILE EXPLORER
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "open file explorer",
        "open explorer",
        "open my files"
    ]):

        try:

            subprocess.Popen(["explorer"])

            return "Opening File Explorer."

        except Exception:

            return "I couldn't open File Explorer."


    # --------------------------------------------------------
    # DOWNLOADS
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "open downloads",
        "open my downloads",
        "show downloads"
    ]):

        try:

            downloads = os.path.join(
                os.path.expanduser("~"),
                "Downloads"
            )

            subprocess.Popen(
                ["explorer", downloads]
            )

            return "Opening your Downloads folder."

        except Exception:

            return "I couldn't open your Downloads folder."


    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "take a screenshot",
        "take screenshot",
        "capture my screen",
        "screenshot"
    ]):

        try:

            import pyautogui

            screenshots_folder = os.path.join(
                os.path.expanduser("~"),
                "Pictures",
                "NOVA Screenshots"
            )

            os.makedirs(
                screenshots_folder,
                exist_ok=True
            )

            filename = datetime.now().strftime(
                "nova_%Y%m%d_%H%M%S.png"
            )

            filepath = os.path.join(
                screenshots_folder,
                filename
            )

            screenshot = pyautogui.screenshot()

            screenshot.save(filepath)

            return "Screenshot saved successfully."

        except Exception as error:

            print(
                "Screenshot error:",
                error
            )

            return "I couldn't take the screenshot."


    # --------------------------------------------------------
    # LOCK COMPUTER
    # --------------------------------------------------------

    if any(phrase in text for phrase in [
        "lock my computer",
        "lock the computer",
        "lock my pc"
    ]):

        subprocess.Popen(
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation"
            ]
        )

        return "Locking your computer."


    # --------------------------------------------------------
    # NO LOCAL COMMAND
    # --------------------------------------------------------

    return None


# ============================================================
# GEMINI
# ============================================================

print("Connecting to Gemini...")

client = genai.Client()

chat = client.chats.create(

    model="gemini-3.6-flash",

    config={

        "system_instruction": """
You are NOVA, a personal AI voice assistant.

Your name is NOVA.

Gemini is the AI model powering you.
You are not Gemini.

If the user asks your name, say your name is NOVA.

If the user asks who you are, say you are NOVA,
their personal AI assistant.

If the user asks what powers you,
explain that you are powered by Google's Gemini AI model.

Never introduce yourself as Gemini.

Never claim to be human.

Never invent information about your creator.

Be helpful, natural, and concise.

You are a desktop AI assistant.
"""
    }
)


# ============================================================
# TEXT TO SPEECH
# ============================================================

print("Initializing voice system...")

tts = pyttsx3.init()

tts.setProperty(
    "rate",
    175
)


# ============================================================
# WHISPER
# ============================================================

print()
print("Loading Whisper model...")
print("This may take a little while on CPU.")
print()

model = whisper.load_model("base")

print("Whisper loaded.")


# ============================================================
# START NOVA
# ============================================================

print()
print("========================================")
print("             NOVA ONLINE")
print("========================================")
print("Microphone device:", MICROPHONE_DEVICE)
print()
print("NOVA will shut down after")
print("5 seconds without speech.")
print("Say 'stop nova' to shut down manually.")
print("========================================")
print()


set_state("idle")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # LISTENING
    # --------------------------------------------------------

    set_state("listening")

    print()
    print("🎤 Listening...")
    print("You have 5 seconds to speak.")


    try:

        audio = sd.rec(

            int(
                SILENCE_TIMEOUT *
                SAMPLE_RATE
            ),

            samplerate=SAMPLE_RATE,

            channels=1,

            dtype="int16",

            device=MICROPHONE_DEVICE
        )

        sd.wait()


    except sd.PortAudioError as error:

        print()
        print("🎤 Microphone temporarily unavailable.")
        print("Error:", error)
        print("Retrying...")
        print()

        set_state("idle")

        continue


    except Exception as error:

        print()
        print("❌ Microphone error:")
        print(error)
        print()

        set_state("idle")

        continue


    # --------------------------------------------------------
    # CHECK WHETHER USER SPOKE
    # --------------------------------------------------------

    audio_float = audio.astype(
        np.float32
    )

    rms = np.sqrt(
        np.mean(
            audio_float ** 2
        )
    )


    print(
        f"Audio level: {rms:.0f}"
    )


    # --------------------------------------------------------
    # NO SPEECH
    # --------------------------------------------------------

    if rms < SPEECH_THRESHOLD:

        print()
        print("🔇 No speech detected for 5 seconds.")

        set_state("speaking")

        print("NOVA: Goodbye.")

        try:

            tts.say(
                "Goodbye."
            )

            tts.runAndWait()

        except Exception as error:

            print(
                "TTS error:",
                error
            )

        set_state("idle")

        print()
        print("========================================")
        print("              NOVA OFFLINE")
        print("========================================")
        print()

        break


    # --------------------------------------------------------
    # SAVE AUDIO
    # --------------------------------------------------------

    try:

        wav.write(
            AUDIO_FILE,
            SAMPLE_RATE,
            audio
        )

    except Exception as error:

        print()
        print("❌ Could not save audio:")
        print(error)
        print()

        set_state("idle")

        continue


    # --------------------------------------------------------
    # WHISPER
    # --------------------------------------------------------

    print()
    print("🧠 Understanding...")

    set_state("thinking")


    try:

        result = model.transcribe(
            AUDIO_FILE
        )

        user_text = result["text"].strip()


    except Exception as error:

        print()
        print("❌ Whisper error:")
        print(error)
        print()

        set_state("idle")

        continue


    # --------------------------------------------------------
    # EMPTY TRANSCRIPTION
    # --------------------------------------------------------

    if not user_text:

        print("I couldn't understand that.")

        set_state("idle")

        continue


    # --------------------------------------------------------
    # SHOW USER
    # --------------------------------------------------------

    print()
    print("You:", user_text)
    print()


    # --------------------------------------------------------
    # MANUAL STOP
    # --------------------------------------------------------

    if "stop nova" in user_text.lower():

        print("NOVA: Shutting down.")

        set_state("speaking")

        try:

            tts.say(
                "Shutting down."
            )

            tts.runAndWait()

        except Exception as error:

            print("TTS error:", error)

        set_state("idle")

        break


    # --------------------------------------------------------
    # LOCAL COMMAND
    # --------------------------------------------------------

    local_response = handle_local_command(
        user_text
    )


    # ========================================================
    # GENERATE RESPONSE
    # ========================================================

    if local_response is not None:

        print(
            "⚡ NOVA handled this locally."
        )

        ai_response = local_response


    else:

        print("🤖 NOVA is thinking...")

        set_state("thinking")


        try:

            response = chat.send_message(
                user_text
            )

            ai_response = response.text


        except Exception as error:

            print()
            print("❌ Gemini error:")
            print(error)
            print()

            ai_response = (
                "Sorry, I couldn't connect "
                "to my AI brain."
            )


    # ========================================================
    # DISPLAY RESPONSE
    # ========================================================

    print()
    print("NOVA:")
    print(ai_response)
    print()


    # ========================================================
    # SPEAK
    # ========================================================

    set_state("speaking")

    print("🔊 NOVA is speaking...")


    try:

        tts.say(
            ai_response
        )

        tts.runAndWait()


    except Exception as error:

        print()
        print("❌ TTS error:")
        print(error)
        print()


    # ========================================================
    # BACK TO LISTENING
    # ========================================================

    set_state("idle")

    print()
    print("----------------------------------------")