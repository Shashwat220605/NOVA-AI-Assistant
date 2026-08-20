"""Lightweight, Windows-focused desktop automation tools for NOVA.

Actions run only when explicitly requested. No background polling, OCR,
browser drivers, or heavy automation services are used.
"""

import os
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

HOME = Path.home()
PICTURES = HOME / "Pictures"
SCREENSHOT_DIR = PICTURES / "NOVA Screenshots"
APP_ALIASES = {
    "chrome": [Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Google/Chrome/Application/chrome.exe", Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "Google/Chrome/Application/chrome.exe"],
    "vscode": [Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Microsoft VS Code/Code.exe"],
}
SITE_ALIASES = {"youtube":"https://www.youtube.com", "github":"https://github.com", "google":"https://www.google.com", "chatgpt":"https://chatgpt.com", "gmail":"https://mail.google.com", "google drive":"https://drive.google.com"}


def _launch(path_or_command, args=None):
    try:
        subprocess.Popen([str(path_or_command), *(args or [])])
        return True
    except (OSError, FileNotFoundError):
        return False


def open_application(name: str) -> str:
    name = name.lower().strip()
    if name in {"chrome", "google chrome"}:
        for path in APP_ALIASES["chrome"]:
            if path.exists() and _launch(path): return "Opening Google Chrome."
        return "I couldn't find Google Chrome."
    if name in {"vs code", "visual studio code", "vscode"}:
        for path in APP_ALIASES["vscode"]:
            if path.exists() and _launch(path): return "Opening Visual Studio Code."
        return "I couldn't find Visual Studio Code."
    commands = {"file explorer":["explorer.exe"], "explorer":["explorer.exe"], "notepad":["notepad.exe"], "calculator":["calc.exe"], "calc":["calc.exe"], "settings":["explorer.exe", "ms-settings:"]}
    command = commands.get(name)
    if command and _launch(command[0], command[1:]): return f"Opening {name}."
    if name == "discord":
        update = Path(os.environ.get("LOCALAPPDATA", "")) / "Discord/Update.exe"
        if update.exists() and _launch(update, ["--processStart", "Discord.exe"]): return "Opening Discord."
        try: os.startfile("discord://"); return "Opening Discord."
        except OSError: return "I couldn't find Discord."
    if name == "spotify":
        try: os.startfile("spotify:"); return "Opening Spotify."
        except OSError: return "I couldn't open Spotify."
    return "That application isn't in NOVA's safe app list."


def open_folder(folder: str) -> str:
    folders = {"desktop":HOME/"Desktop", "downloads":HOME/"Downloads", "documents":HOME/"Documents", "pictures":PICTURES, "music":HOME/"Music", "videos":HOME/"Videos"}
    path = folders.get(folder.lower().strip())
    if path is None: return "That folder isn't in NOVA's safe folder list."
    if not path.exists(): return f"I couldn't find your {folder} folder."
    return "Opening your folder." if _launch("explorer.exe", [str(path)]) else "I couldn't open that folder."


def get_active_window() -> str:
    if os.name != "nt": return "Active-window detection is currently supported on Windows only."
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value.strip()
        return f"The active window is {title}." if title else "I couldn't identify the active window."
    except Exception as error:
        print("Active window error:", error); return "I couldn't identify the active window."


def _foreground_hwnd():
    if os.name != "nt": return None
    import ctypes
    return ctypes.windll.user32.GetForegroundWindow()


def control_window(action: str) -> str:
    """Perform a lightweight foreground-window action through Win32."""
    if os.name != "nt": return "Window control is currently supported on Windows only."
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = _foreground_hwnd()
        if not hwnd: return "I couldn't identify the active window."
        if action == "minimize": user32.ShowWindow(hwnd, 6); return "Window minimized."
        if action == "maximize": user32.ShowWindow(hwnd, 3); return "Window maximized."
        if action == "close": user32.PostMessageW(hwnd, 0x0010, 0, 0); return "Window close requested."
        if action in {"left", "right"}:
            screen_w = user32.GetSystemMetrics(0); screen_h = user32.GetSystemMetrics(1)
            half = screen_w // 2
            x = 0 if action == "left" else half
            user32.SetWindowPos(hwnd, 0, x, 0, half, screen_h, 0x0040)
            return f"Window moved {action}."
        if action.startswith("switch:"):
            title = action.split(":", 1)[1].strip().lower()
            found = None
            def callback(handle, _):
                nonlocal found
                length = user32.GetWindowTextLengthW(handle)
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(handle, buf, length + 1)
                if title and title in buf.value.lower(): found = handle; return False
                return True
            user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(callback), 0)
            if found:
                user32.ShowWindow(found, 9); user32.SetForegroundWindow(found); return f"Switched to {title}."
            return f"I couldn't find a window matching {title}."
        return "That window action isn't supported."
    except Exception as error:
        print("Window control error:", error); return "I couldn't control that window."


def take_screenshot() -> str:
    try:
        import pyautogui
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        path = SCREENSHOT_DIR / datetime.now().strftime("nova_%Y%m%d_%H%M%S.png")
        pyautogui.screenshot().save(path); return f"Screenshot saved to {path}."
    except Exception as error:
        print("Screenshot error:", error); return "I couldn't take the screenshot."


def control_media(action: str) -> str:
    keys = {"play":"playpause", "pause":"playpause", "playpause":"playpause", "next":"nexttrack", "previous":"prevtrack"}
    key = keys.get(action)
    if not key: return "That media action isn't supported."
    try:
        import pyautogui; pyautogui.press(key); return f"Media {action}."
    except Exception as error: print("Media control error:", error); return "I couldn't control media."


def control_volume(action: str) -> str:
    keys = {"up":"volumeup", "down":"volumedown", "mute":"volumemute"}
    key = keys.get(action)
    if not key: return "That volume action isn't supported."
    try:
        import pyautogui; pyautogui.press(key); return {"up":"Volume increased.", "down":"Volume decreased.", "mute":"Volume muted or unmuted."}[action]
    except Exception as error: print("Volume control error:", error); return "I couldn't control the volume."


def open_site(name: str) -> str:
    url = SITE_ALIASES.get(name.lower().strip())
    return open_url(url) if url else "That site isn't in NOVA's safe website list."


def open_url(url: str) -> str:
    if not url.startswith(("https://", "http://")): url = "https://" + url
    try: webbrowser.open(url); return "Opening the website."
    except Exception: return "I couldn't open that website."


def web_search(query: str, site: str | None = None) -> str:
    if not query.strip(): return "Tell me what you want me to search for."
    base = "https://www.youtube.com/results?search_query=" if site == "youtube" else "https://www.google.com/search?q="
    return open_url(base + quote_plus(query))


def create_folder(name: str) -> str:
    safe_name = Path(name.strip()).name
    if not safe_name or safe_name in {".", ".."}: return "Please provide a valid folder name."
    base = HOME / "Desktop" / "NOVA"
    try:
        base.mkdir(exist_ok=True); (base / safe_name).mkdir(exist_ok=True); return f"Created the folder {safe_name} on your Desktop in NOVA."
    except OSError: return "I couldn't create that folder."


def lock_computer() -> str:
    try: subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"]); return "Locking your computer."
    except OSError: return "I couldn't lock your computer."


def power_action(action: str) -> str:
    commands = {"shutdown":["shutdown","/s","/t","0"], "restart":["shutdown","/r","/t","0"], "sleep":["rundll32.exe","powrprof.dll,SetSuspendState","0,1,0"]}
    command = commands.get(action)
    if not command: return "That power action isn't supported."
    try: subprocess.Popen(command); return f"Starting {action}."
    except OSError: return f"I couldn't start {action}."


def available_tools() -> list[str]:
    return ["open_application","open_folder","get_active_window","control_window","take_screenshot","control_media","control_volume","open_site","open_url","web_search","create_folder","lock_computer","power_action"]
