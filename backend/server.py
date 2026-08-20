import os
import sys
import subprocess
import platform
import psutil
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.confirmation_store import clear_pending, get_pending
from backend.desktop_automation import create_folder, power_action

app = FastAPI(title="NOVA AI", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.abspath(os.path.join(BASE_DIR, ".."))
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")
VOICE_EXE = os.path.join(ROOT_DIR, "dist", "voice_ai", "voice_ai.exe")
nova_state = {"state": "idle", "message": "Ready.", "confirmation": None}
voice_process = None
assets_directory = os.path.join(FRONTEND_DIST, "assets")
telemetry_cache = None
telemetry_cache_time = 0.0
network_sample = None

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
    return nova_state

@app.post("/state/{state}")
def update_state(state: str, payload: dict | None = None):
    messages = {"idle": "Ready.", "listening": "Listening for your voice.", "thinking": "NOVA is thinking.", "speaking": "NOVA is speaking.", "executing": "Executing desktop action.", "success": "Action completed successfully.", "error": "Desktop action failed.", "confirmation": "Confirmation required."}
    nova_state["state"] = state
    nova_state["message"] = (payload or {}).get("message") or messages.get(state, "NOVA is active.")
    if state == "confirmation":
        nova_state["confirmation"] = (payload or {}).get("confirmation")
    elif state not in {"speaking", "listening", "thinking"}:
        nova_state["confirmation"] = None
    return {"success": True, **nova_state}

@app.post("/confirm")
def confirm_action():
    pending = get_pending()
    if not pending:
        return {"success": False, "message": "There is no pending action."}
    try:
        if pending["action"] == "power":
            result = power_action(pending["argument"])
        elif pending["action"] == "create_folder":
            result = create_folder(pending["argument"])
        else:
            clear_pending()
            nova_state["state"] = "error"
            nova_state["message"] = "Unsupported protected action."
            return {"success": False, "message": nova_state["message"]}
        clear_pending()
        nova_state["confirmation"] = None
        nova_state["state"] = "success"
        nova_state["message"] = result
        return {"success": True, "message": result}
    except Exception as error:
        clear_pending()
        nova_state["confirmation"] = None
        nova_state["state"] = "error"
        nova_state["message"] = "The action could not be completed."
        return {"success": False, "message": str(error)}

@app.post("/cancel")
def cancel_action():
    clear_pending()
    nova_state["confirmation"] = None
    nova_state["state"] = "idle"
    nova_state["message"] = "Action cancelled."
    return {"success": True, "message": "Action cancelled."}

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
        nova_state["message"] = "Ready."
        return {"success": True, "message": "NOVA voice system stopped."}
    except Exception as error:
        return {"success": False, "message": str(error)}


def _network_speed():
    global network_sample
    now = time.monotonic()
    current = psutil.net_io_counters()
    if network_sample is None:
        network_sample = (now, current.bytes_sent, current.bytes_recv)
        return {"upload_kbps": 0.0, "download_kbps": 0.0}
    old_time, old_sent, old_recv = network_sample
    elapsed = max(now - old_time, 0.001)
    network_sample = (now, current.bytes_sent, current.bytes_recv)
    return {
        "upload_kbps": round((current.bytes_sent - old_sent) / elapsed / 1024, 1),
        "download_kbps": round((current.bytes_recv - old_recv) / elapsed / 1024, 1),
    }


def _gpu_telemetry():
    data = {"name": "NVIDIA GPU", "percent": None, "vram_used_mb": None, "vram_total_mb": None, "temperature_c": None}
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=1.0,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = [p.strip() for p in result.stdout.splitlines()[0].split(",")]
            if len(parts) >= 5:
                data = {"name": parts[0], "percent": float(parts[1]), "vram_used_mb": float(parts[2]), "vram_total_mb": float(parts[3]), "temperature_c": float(parts[4])}
    except Exception:
        pass
    return data

@app.get("/system")
def get_system_telemetry():
    global telemetry_cache, telemetry_cache_time
    now = time.monotonic()
    if telemetry_cache is not None and now - telemetry_cache_time < 3.0:
        return telemetry_cache

    memory = psutil.virtual_memory()
    drive = os.environ.get("SystemDrive") or "C:"
    disk = psutil.disk_usage(drive + "\\")
    battery = psutil.sensors_battery()
    cpu_temp = None
    try:
        temps = psutil.sensors_temperatures()
        for entries in temps.values():
            if entries:
                cpu_temp = round(entries[0].current, 1)
                break
    except Exception:
        pass

    gpu = _gpu_telemetry()
    telemetry_cache = {
        "ram": {"total": round(memory.total / 1024**3, 1), "used": round(memory.used / 1024**3, 1), "available": round(memory.available / 1024**3, 1), "percent": memory.percent},
        "storage": {"drive": drive, "total": round(disk.total / 1024**3, 1), "used": round(disk.used / 1024**3, 1), "free": round(disk.free / 1024**3, 1), "percent": disk.percent},
        "cpu": {"name": platform.processor() or "Unknown CPU", "percent": psutil.cpu_percent(interval=None), "temperature_c": cpu_temp},
        "gpu": gpu,
        "network": _network_speed(),
        "battery": {"percent": battery.percent if battery else None, "plugged": battery.power_plugged if battery else None},
        "system": {"name": f"{platform.system()} {platform.release()}" if platform.system() == "Windows" else platform.system()},
    }
    telemetry_cache_time = now
    return telemetry_cache

@app.get("/health")
def health():
    global voice_process
    voice_running = voice_process is not None and voice_process.poll() is None
    return {"status": "online", "voice_system": "running" if voice_running else "offline", "frontend": "available" if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")) else "missing"}

@app.get("/debug")
def debug():
    return {"root_dir": ROOT_DIR, "frontend": FRONTEND_DIST, "voice_exe": VOICE_EXE, "voice_exists": os.path.exists(VOICE_EXE), "frontend_exists": os.path.exists(os.path.join(FRONTEND_DIST, "index.html"))}
