import os
import sys
import subprocess
import platform
import psutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="NOVA AI", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(os.path.join(BASE_DIR, ".."))
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")
VOICE_EXE = os.path.join(ROOT_DIR, "dist", "voice_ai", "voice_ai.exe")

nova_state = {"state": "idle", "message": "Ready."}
voice_process = None

assets_directory = os.path.join(FRONTEND_DIST, "assets")
if os.path.exists(assets_directory):
    app.mount("/assets", StaticFiles(directory=assets_directory), name="assets")

@app.get("/")
def serve_frontend():
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "NOVA backend is running.", "frontend": "Not built."}

@app.get("/state")
def get_state():
    global voice_process
    if voice_process is not None and voice_process.poll() is not None:
        voice_process = None
        if nova_state["state"] in ["listening", "thinking", "speaking", "executing"]:
            nova_state["state"] = "idle"
            nova_state["message"] = "Ready."
    return nova_state

@app.post("/state/{state}")
def update_state(state: str):
    messages = {
        "idle": "Ready.",
        "listening": "Listening for your voice.",
        "thinking": "NOVA is thinking.",
        "speaking": "NOVA is speaking.",
        "executing": "Executing desktop action.",
        "success": "Action completed successfully.",
        "error": "Desktop action failed.",
    }
    nova_state["state"] = state
    nova_state["message"] = messages.get(state, "NOVA is active.")
    return {"success": True, "state": state, "message": nova_state["message"]}

@app.post("/listen")
def start_listening():
    global voice_process
    if voice_process is not None and voice_process.poll() is None:
        return {"success": False, "message": "NOVA is already listening."}
    if not os.path.exists(VOICE_EXE):
        return {"success": False, "message": "voice_ai.exe was not found."}
    try:
        voice_process = subprocess.Popen([VOICE_EXE], cwd=os.path.dirname(VOICE_EXE), creationflags=subprocess.CREATE_NEW_CONSOLE)
        nova_state["state"] = "listening"
        nova_state["message"] = "Listening for your voice."
        return {"success": True, "message": "NOVA voice system started."}
    except Exception as error:
        return {"success": False, "message": str(error)}

@app.post("/stop")
def stop_listening():
    global voice_process
    if voice_process is None or voice_process.poll() is not None:
        voice_process = None
        nova_state["state"] = "idle"
        nova_state["message"] = "Ready."
        return {"success": False, "message": "NOVA is not running."}
    try:
        voice_process.terminate()
        try:
            voice_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            voice_process.kill()
            voice_process.wait()
        voice_process = None
        nova_state["state"] = "idle"
        nova_state["message"] = "NOVA is offline."
        return {"success": True, "message": "NOVA voice system stopped."}
    except Exception as error:
        return {"success": False, "message": str(error)}

@app.get("/system")
def get_system_telemetry():
    memory = psutil.virtual_memory()
    drive = os.environ.get("SystemDrive", "C:")
    disk = psutil.disk_usage(drive + "\\")
    cpu_name = platform.processor() or "Unknown CPU"
    gpu_name = "NVIDIA GPU"
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout.strip():
            gpu_name = result.stdout.strip().splitlines()[0]
    except Exception:
        pass
    windows_version = platform.system()
    if windows_version == "Windows":
        windows_version = f"Windows {platform.release()}"
    return {
        "ram": {"total": round(memory.total / 1024**3, 1), "used": round(memory.used / 1024**3, 1), "available": round(memory.available / 1024**3, 1), "percent": memory.percent},
        "storage": {"drive": drive, "total": round(disk.total / 1024**3, 1), "used": round(disk.used / 1024**3, 1), "free": round(disk.free / 1024**3, 1), "percent": disk.percent},
        "cpu": {"name": cpu_name, "percent": psutil.cpu_percent(interval=None)},
        "gpu": {"name": gpu_name},
        "system": {"name": windows_version},
    }

@app.get("/health")
def health():
    global voice_process
    voice_running = voice_process is not None and voice_process.poll() is None
    return {"status": "online", "voice_system": "running" if voice_running else "offline", "frontend": "available" if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")) else "missing"}

@app.get("/debug")
def debug():
    return {"root_dir": ROOT_DIR, "frontend": FRONTEND_DIST, "voice_exe": VOICE_EXE, "voice_exists": os.path.exists(VOICE_EXE), "frontend_exists": os.path.exists(os.path.join(FRONTEND_DIST, "index.html"))}
