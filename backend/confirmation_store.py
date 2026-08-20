"""Tiny file-based IPC for confirmation-gated NOVA actions.

The voice process and FastAPI process are separate Windows processes, so a
small JSON file in the user's temp directory is enough. It creates no daemon,
no database, and no background worker.
"""

import json
import os
import tempfile
from pathlib import Path

STORE = Path(tempfile.gettempdir()) / "nova_pending_action.json"


def set_pending(action: str, argument: str = "", label: str = "") -> None:
    payload = {"action": action, "argument": argument, "label": label}
    STORE.write_text(json.dumps(payload), encoding="utf-8")


def get_pending() -> dict | None:
    try:
        if not STORE.exists():
            return None
        return json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def clear_pending() -> None:
    try:
        STORE.unlink(missing_ok=True)
    except OSError:
        pass
