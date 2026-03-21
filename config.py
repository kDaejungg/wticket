from dotenv import load_dotenv
import os
import json

load_dotenv()

def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"[WTicket] '{key}' is missing or empty in .env!")
    return val

TOKEN: str = _require("BOT_TOKEN")

SETTINGS_FILE = "settings.json"

_defaults = {
    "TICKET_CHANNEL_ID": None,
    "STAFF_ROLE_ID": None,
    "PING_ROLE_ID": None,
}

def _load() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return dict(_defaults)
    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)
    return {**_defaults, **data}

def _save(data: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get(key: str):
    return _load().get(key)

def set(key: str, value):
    data = _load()
    data[key] = value
    _save(data)

def is_configured() -> bool:
    data = _load()
    return bool(data.get("TICKET_CHANNEL_ID") and data.get("STAFF_ROLE_ID"))
