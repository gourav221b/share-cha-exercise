"""
Standalone reference app for reviewers.

  uvicorn reference.app:app --reload --port 8766

Uses the same static UI and data/ folders as the candidate starter.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import store
from reference.snapshot import build_public_snapshot

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"

app = FastAPI(title="Share Chat Reference", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CreateShareRequest(BaseModel):
    chat_id: str = Field(..., min_length=1)
    ttl_days: Optional[int] = Field(default=30, ge=1, le=365)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _is_expired(payload: Dict[str, Any]) -> bool:
    exp = _parse_iso(payload.get("expires_at"))
    return bool(exp and exp <= _now())


def _find_active_share_for_chat(chat_id: str) -> Optional[Dict[str, Any]]:
    for path in store.list_share_files():
        try:
            data = store.read_share(path.stem)
        except Exception:
            continue
        if not data:
            continue
        if data.get("chat_id") != chat_id:
            continue
        if data.get("revoked"):
            continue
        if _is_expired(data):
            continue
        return data
    return None


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/share/{token}")
def share_page(token: str) -> FileResponse:
    return FileResponse(STATIC_DIR / "share.html")


@app.get("/api/chats")
def list_chats() -> Dict[str, Any]:
    chats = store.load_chats()
    return {
        "chats": [
            {
                "id": c["id"],
                "title": c.get("title") or "Untitled",
                "owner_id": c.get("owner_id"),
                "message_count": len(c.get("messages") or []),
            }
            for c in chats
        ]
    }


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str) -> Dict[str, Any]:
    chat = store.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@app.post("/api/shares", status_code=201)
def create_share(body: CreateShareRequest) -> Dict[str, Any]:
    chat = store.get_chat(body.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    existing = _find_active_share_for_chat(body.chat_id)
    if existing:
        token = existing["token"]
        return {
            "token": token,
            "url": f"/share/{token}",
            "title": existing.get("title"),
            "expires_at": existing.get("expires_at"),
        }

    snapshot = build_public_snapshot(chat)
    token = secrets.token_urlsafe(16)
    created = _now()
    expires = created + timedelta(days=body.ttl_days or 30)
    payload = {
        "token": token,
        "chat_id": body.chat_id,
        "title": snapshot["title"],
        "snapshot": snapshot,
        "created_at": created.isoformat(),
        "expires_at": expires.isoformat(),
        "revoked": False,
    }
    store.write_share(token, payload)
    return {
        "token": token,
        "url": f"/share/{token}",
        "title": snapshot["title"],
        "expires_at": payload["expires_at"],
    }


@app.get("/api/shares/{token}")
def get_share(token: str) -> Dict[str, Any]:
    data = store.read_share(token)
    if not data or data.get("revoked") or _is_expired(data):
        raise HTTPException(status_code=404, detail="Share not found")
    snapshot = data.get("snapshot") or {}
    return {
        "title": data.get("title") or snapshot.get("title") or "Shared chat",
        "snapshot": snapshot,
        "expires_at": data.get("expires_at"),
    }


@app.delete("/api/shares/{token}")
def revoke_share(token: str) -> Dict[str, Any]:
    data = store.read_share(token)
    if not data:
        raise HTTPException(status_code=404, detail="Share not found")
    data["revoked"] = True
    store.write_share(token, data)
    return {"ok": True}
