import os
import sys
import subprocess
import platform
import psutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="NOVA AI",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


if getattr(sys, "frozen", False):

    ROOT_DIR = sys._MEIPASS

else:

    ROOT_DIR = os.path.abspath(
        os.path.join(
            BASE_DIR,
            ".."
        )
    )


FRONTEND_DIST = os.path.join(
    ROOT_DIR,
    "frontend",
    "dist"
)


VOICE_EXE = os.path.join(
    ROOT_DIR,
    "dist",
    "voice_ai",
    "voice_ai.exe"
)


# ============================================================
# NOVA STATE
# ============================================================

nova_state = {
    "state": "idle",
    "message": "Ready."
}


voice_process = None


# ============================================================
# FRONTEND
# ============================================================

assets_directory = os.path.join(
    FRONTEND_DIST,
    "assets"
)


if os.path.exists(assets_directory):

    app.mount(
        "/assets",
        StaticFiles(
            directory=assets_directory
        ),
        name="assets"
    )


@app.get("/")
def serve_frontend():

    index_file = os.path.join(
        FRONTEND_DIST,
        "index.html"
    )


    if os.path.exists(index_file):

        return FileResponse(
            index_file
        )


    return {
        "message": "NOVA backend is running.",
        "frontend": "Not built."
    }


# ============================================================
# NOVA STATE
# ============================================================

@app.get("/state")
def get_state():

    global voice_process


    if (
        voice_process is not None
        and voice_process.poll() is not None
    ):

        voice_process = None

        if nova_state["state"] in [
            "listening",
            "thinking",
            "speaking"
        ]:

            nova_state["state"] = "idle"
            nova_state["message"] = "Ready."


    return nova_state


# ============================================================
# UPDATE STATE
# ============================================================

@app.post("/state/{state}")
def update_state(state: str):

    messages = {

        "idle":
            "Ready.",

        "listening":
            "Listening for your voice.",

        "thinking":
            "NOVA is thinking.",

        "speaking":
            "NOVA is speaking."

    }


    nova_state["state"] = state

    nova_state["message"] = messages.get(
        state,
        "NOVA is active."
    )


    return {
        "success": True,
        "state": state,
        "message": nova_state["message"]
    }


# ============================================================
# START VOICE AI
# ============================================================

@app.post("/listen")
def start_listening():

    global voice_process


    if (
        voice_process is not None
        and voice_process.poll() is None
    ):

        return {
            "success": False,
            "message": "NOVA is already listening."
        }


    if not os.path.exists(VOICE_EXE):

        print()
        print("VOICE EXE NOT FOUND")
        print(VOICE_EXE)
        print()

        return {
            "success": False,
            "message": "voice_ai.exe was not found."
        }


    try:

        print()
        print("STARTING NOVA VOICE AI")
        print(VOICE_EXE)
        print()


        voice_process = subprocess.Popen(

            [VOICE_EXE],

            cwd=os.path.dirname(
                VOICE_EXE
            ),

            # Keep this as CREATE_NEW_CONSOLE
            # while testing the packaged version.
            creationflags=subprocess.CREATE_NEW_CONSOLE

        )


        nova_state["state"] = "listening"

        nova_state["message"] = (
            "Listening for your voice."
        )


        print(
            "voice_ai.exe started."
        )

        print(
            "PID:",
            voice_process.pid
        )


        return {
            "success": True,
            "message": "NOVA voice system started."
        }


    except Exception as error:

        print(
            "FAILED TO START VOICE AI:"
        )

        print(error)


        return {
            "success": False,
            "message": str(error)
        }


# ============================================================
# STOP VOICE AI
# ============================================================

@app.post("/stop")
def stop_listening():

    global voice_process


    if (
        voice_process is None
        or voice_process.poll() is not None
    ):

        voice_process = None

        nova_state["state"] = "idle"
        nova_state["message"] = "Ready."


        return {
            "success": False,
            "message": "NOVA is not running."
        }


    try:

        voice_process.terminate()

        try:

            voice_process.wait(
                timeout=3
            )

        except subprocess.TimeoutExpired:

            voice_process.kill()

            voice_process.wait()


        voice_process = None


        nova_state["state"] = "idle"

        nova_state["message"] = (
            "NOVA is offline."
        )


        return {
            "success": True,
            "message": "NOVA voice system stopped."
        }


    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }


# ============================================================
# SYSTEM TELEMETRY
# ============================================================

@app.get("/system")
def get_system_telemetry():

    # --------------------------------------------------------
    # RAM
    # --------------------------------------------------------

    memory = psutil.virtual_memory()

    ram_total_gb = memory.total / (
        1024 ** 3
    )

    ram_used_gb = memory.used / (
        1024 ** 3
    )

    ram_available_gb = memory.available / (
        1024 ** 3
    )

    ram_percent = memory.percent


    # --------------------------------------------------------
    # CPU
    # --------------------------------------------------------

    cpu_percent = psutil.cpu_percent(
        interval=None
    )


    # --------------------------------------------------------
    # STORAGE
    # --------------------------------------------------------

    drive = os.environ.get(
        "SystemDrive",
        "C:"
    )


    disk = psutil.disk_usage(
        drive + "\\"
    )


    disk_total_gb = disk.total / (
        1024 ** 3
    )

    disk_used_gb = disk.used / (
        1024 ** 3
    )

    disk_free_gb = disk.free / (
        1024 ** 3
    )

    disk_percent = disk.percent


    # --------------------------------------------------------
    # CPU NAME
    # --------------------------------------------------------

    cpu_name = platform.processor()

    if not cpu_name:

        cpu_name = "Unknown CPU"


    # --------------------------------------------------------
    # GPU
    # --------------------------------------------------------

    gpu_name = "NVIDIA GPU"

    try:

        result = subprocess.run(

            [
                "nvidia-smi",
                "--query-gpu=name",
                "--format=csv,noheader"
            ],

            capture_output=True,

            text=True,

            timeout=2

        )


        if result.returncode == 0:

            detected_gpu = (
                result.stdout
                .strip()
                .splitlines()
            )


            if detected_gpu:

                gpu_name = detected_gpu[0]


    except Exception:

        pass


    # --------------------------------------------------------
    # WINDOWS
    # --------------------------------------------------------

    windows_version = platform.system()

    release = platform.release()

    if windows_version == "Windows":

        windows_version = (
            f"Windows {release}"
        )


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {

        "ram": {

            "total": round(
                ram_total_gb,
                1
            ),

            "used": round(
                ram_used_gb,
                1
            ),

            "available": round(
                ram_available_gb,
                1
            ),

            "percent": ram_percent

        },


        "storage": {

            "drive": drive,

            "total": round(
                disk_total_gb,
                1
            ),

            "used": round(
                disk_used_gb,
                1
            ),

            "free": round(
                disk_free_gb,
                1
            ),

            "percent": disk_percent

        },


        "cpu": {

            "name": cpu_name,

            "percent": cpu_percent

        },


        "gpu": {

            "name": gpu_name

        },


        "system": {

            "name": windows_version

        }

    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    global voice_process


    voice_running = (

        voice_process is not None

        and voice_process.poll() is None

    )


    return {

        "status":
            "online",

        "voice_system":

            "running"

            if voice_running

            else "offline",

        "frontend":

            "available"

            if os.path.exists(
                os.path.join(
                    FRONTEND_DIST,
                    "index.html"
                )
            )

            else "missing"

    }


# ============================================================
# DEBUG
# ============================================================

@app.get("/debug")
def debug():

    return {

        "root_dir":
            ROOT_DIR,

        "frontend":
            FRONTEND_DIST,

        "voice_exe":
            VOICE_EXE,

        "voice_exists":
            os.path.exists(
                VOICE_EXE
            ),

        "frontend_exists":
            os.path.exists(
                os.path.join(
                    FRONTEND_DIST,
                    "index.html"
                )
            )

    }