import sounddevice as sd

print("Recording device:")
print(sd.query_devices())

print("\nDefault input device:")
print(sd.default.device)