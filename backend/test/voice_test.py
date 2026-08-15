import sounddevice as sd
import scipy.io.wavfile as wav
import whisper
import os

SAMPLE_RATE = 16000
RECORD_SECONDS = 5
AUDIO_FILE = "voice.wav"

print("Loading Whisper model...")
model = whisper.load_model("base")

print("\n==============================")
print("        NOVA IS READY")
print("==============================")
print("Speak a command.")
print("Say 'Nova, stop' to exit.\n")


while True:

    print("🎤 Listening...")

    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    wav.write(AUDIO_FILE, SAMPLE_RATE, audio)

    print("🧠 Processing...")

    result = model.transcribe(AUDIO_FILE)

    text = result["text"].strip()

    if not text:
        print("Didn't hear anything.\n")
        continue

    print(f"\nYou: {text}")

    if "nova" in text.lower() and "stop" in text.lower():
        print("\nNOVA: Shutting down. Goodbye!")
        break

    print("NOVA: I heard you.\n")


if os.path.exists(AUDIO_FILE):
    os.remove(AUDIO_FILE)