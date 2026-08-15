NOVA ERROR ARCHIVE

Distinct screenshot-backed error cases from the NOVA development process. Duplicate root causes were consolidated. Each numbered case contains a representative screenshot and a detailed solution text file.

01. PowerShell virtual-environment activation blocked -> 01_powershell_execution_policy
02. Python modules missing from the active virtual environment -> 02_missing_sounddevice_and_whisper
03. Whisper failed while loading voice.wav -> 03_whisper_audio_loading_ffmpeg
04. OpenAI API returned 429 insufficient_quota -> 04_openai_quota_429
05. Gemini returned 503 UNAVAILABLE -> 05_gemini_503_high_demand
06. pyttsx3 was not installed in the environment -> 06_missing_pyttsx3
07. webrtcvad-wheels failed to build -> 07_webrtcvad_build_tools
08. sounddevice could not determine input channels -> 08_audio_input_channel_detection
09. Python reported continue can be used only within a loop -> 09_continue_outside_loop
10. PyAutoGUI could not import pyscreeze -> 10_pyautogui_pyscreeze_pillow
11. NOVA launcher could not find server.py after packaging -> 11_server_py_not_found_in_package
12. Packaged voice_ai.exe reported that no Gemini API key was provided -> 12_gemini_api_key_missing
13. Uvicorn failed with Windows error 10048 -> 13_port_8000_already_in_use
14. Windows Smart App Control blocked NOVA.exe -> 14_smart_app_control
