"""File-backed storage helpers. Prefer these over inventing a new persistence layer."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CHATS_PATH = DATA_DIR / "chats.json"
SHARES_DIR = DATA_DIR / "shares"

_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def ensure_shares_dir() -> None:
    SHARES_DIR.mkdir(parents=True, exist_ok=True)


def load_chats() -> List[Dict[str, Any]]:
    with CHATS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("chats.json must be a JSON array")
    return data


def get_chat(chat_id: str) -> Optional[Dict[str, Any]]:
    for chat in load_chats():
        if chat.get("id") == chat_id:
            return chat
    return None


def share_path(token: str) -> Path:
    if not _TOKEN_RE.match(token):
        raise ValueError("invalid share token")
    return SHARES_DIR / f"{token}.json"


def write_share(token: str, payload: Dict[str, Any]) -> None:
    ensure_shares_dir()
    path = share_path(token)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def read_share(token: str) -> Optional[Dict[str, Any]]:
    try:
        path = share_path(token)
    except ValueError:
        return None
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def delete_share(token: str) -> bool:
    try:
        path = share_path(token)
    except ValueError:
        return False
    if not path.exists():
        return False
    path.unlink()
    return True


def list_share_files() -> List[Path]:
    ensure_shares_dir()
    return sorted(SHARES_DIR.glob("*.json"))
