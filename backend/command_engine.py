"""Lightweight intent routing for NOVA.

No local LLM, OCR, embeddings, or continuous processing is used here.
Commands are normalized and routed deterministically to keep CPU/RAM usage low.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Intent:
    name: str
    argument: str = ""
    requires_confirmation: bool = False


APP_ALIASES = {
    "chrome": ("chrome", "google chrome"),
    "vs code": ("vs code", "visual studio code", "vscode"),
    "discord": ("discord",),
    "spotify": ("spotify",),
    "calculator": ("calculator", "calc"),
    "notepad": ("notepad",),
    "file explorer": ("file explorer", "explorer"),
    "settings": ("settings", "windows settings"),
}

FOLDER_ALIASES = {
    "desktop": ("desktop",),
    "downloads": ("downloads", "download"),
    "documents": ("documents", "document"),
    "pictures": ("pictures", "photos"),
    "music": ("music",),
    "videos": ("videos", "video"),
}


def _find_alias(text: str, aliases: dict[str, tuple[str, ...]]) -> str | None:
    for canonical, names in aliases.items():
        if any(name in text for name in names):
            return canonical
    return None


def detect_intent(text: str) -> Intent | None:
    """Convert a spoken sentence into one small, explicit intent."""
    text = " ".join(text.lower().strip().split())
    if not text:
        return None

    if text in {"hello", "hi", "hey", "hello nova", "hi nova", "hey nova"}:
        return Intent("greeting")
    if "stop nova" in text:
        return Intent("stop")
    if any(p in text for p in ("what time is it", "tell me the time", "current time")):
        return Intent("time")
    if any(p in text for p in ("what is your name", "what's your name", "who are you")):
        return Intent("identity")
    if any(p in text for p in ("what can you do", "what are your capabilities", "what do you do")):
        return Intent("capabilities")
    if any(p in text for p in ("are you there", "are you online", "are you working")):
        return Intent("status")

    if any(p in text for p in ("take a screenshot", "take screenshot", "capture my screen", "screenshot")):
        return Intent("screenshot")
    if any(p in text for p in ("lock my computer", "lock the computer", "lock my pc")):
        return Intent("lock")

    media = {
        "next": ("next song", "next track", "skip song", "skip track"),
        "previous": ("previous song", "previous track", "go back song"),
        "play": ("play music", "resume music", "play media"),
        "pause": ("pause music", "pause media"),
    }
    for action, phrases in media.items():
        if any(p in text for p in phrases):
            return Intent("media", action)

    volume = {
        "up": ("volume up", "increase volume", "turn volume up", "louder"),
        "down": ("volume down", "decrease volume", "turn volume down", "quieter"),
        "mute": ("mute volume", "mute computer", "unmute volume", "unmute computer"),
    }
    for action, phrases in volume.items():
        if any(p in text for p in phrases):
            return Intent("volume", action)

    for action, phrases in {
        "shutdown": ("shutdown computer", "shut down computer", "shutdown my computer", "shut down my computer"),
        "restart": ("restart computer", "restart my computer"),
        "sleep": ("put computer to sleep", "sleep computer", "put my computer to sleep"),
    }.items():
        if any(p in text for p in phrases):
            return Intent("power", action, requires_confirmation=True)

    # Check the specific YouTube form before generic web search.
    match = re.search(r"(?:search|find) youtube (?:for )?(.+)", text)
    if match:
        return Intent("youtube_search", match.group(1).strip())

    match = re.search(r"(?:search|google) (?:for )?(.+)", text)
    if match:
        return Intent("web_search", match.group(1).strip())

    match = re.search(r"(?:open|go to|visit)\s+((?:https?://)?(?:www\.)?[^\s]+\.[a-z]{2,}(?:/[^\s]*)?)", text)
    if match:
        return Intent("open_url", match.group(1))

    match = re.search(r"(?:create|make) (?:a )?folder(?: called| named)? (.+)", text)
    if match:
        return Intent("create_folder", match.group(1).strip())

    app = _find_alias(text, APP_ALIASES)
    if app and any(p in text for p in ("open ", "launch ", "start ")):
        return Intent("open_app", app)

    folder = _find_alias(text, FOLDER_ALIASES)
    if folder and any(p in text for p in ("open ", "show ", "view ")):
        return Intent("open_folder", folder)

    return None
