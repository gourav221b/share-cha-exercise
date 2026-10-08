"""
Share-chat take-home API.

Run from the project root:
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8765

Then open http://127.0.0.1:8765/
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import store
from app.snapshot import build_public_snapshot

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"

app = FastAPI(title="Share Chat Take-home", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CreateShareRequest(BaseModel):
    chat_id: str = Field(..., min_length=1)
    # Optional: candidate may honor this for the stretch goal.
    ttl_days: Optional[int] = Field(default=None, ge=1, le=365)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/share/{token}")
def share_page(token: str) -> FileResponse:
    return FileResponse(STATIC_DIR / "share.html")


@app.get("/api/chats")
def list_chats() -> Dict[str, Any]:
    """Return seed chats (already implemented)."""
    chats = store.load_chats()
    summary = [
        {
            "id": c["id"],
            "title": c.get("title") or "Untitled",
            "owner_id": c.get("owner_id"),
            "message_count": len(c.get("messages") or []),
        }
        for c in chats
    ]
    return {"chats": summary}


@app.get("/api/chats/{chat_id}")
def get_chat(chat_id: str) -> Dict[str, Any]:
    chat = store.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@app.post("/api/shares", status_code=201)
def create_share(body: CreateShareRequest) -> Dict[str, Any]:
    """
    TODO (candidate):
    1. Load the chat by body.chat_id (404 if missing).
    2. Build a public snapshot via build_public_snapshot(chat).
    3. Mint a URL-safe token (secrets.token_urlsafe is fine).
    4. Persist a share document with store.write_share(token, payload).
       Suggested payload fields:
         token, chat_id, title, snapshot, created_at (ISO UTC),
         expires_at (ISO UTC or null), revoked (bool, default false)
    5. Return { "token", "url", "title", "expires_at" }
       where url is "/share/{token}".

    If the same chat is shared again, either:
      - return the existing active share, OR
      - create a new token
    Document your choice in the README / PR notes.
    """
    raise HTTPException(
        status_code=501,
        detail="Not implemented: create_share in app/main.py",
    )


@app.get("/api/shares/{token}")
def get_share(token: str) -> Dict[str, Any]:
    """
    TODO (candidate):
    - Load share with store.read_share(token)
    - 404 if missing, revoked, or expired
    - Return a public-safe payload: title + snapshot messages
      (do not leak owner_id or internal file urls)
    """
    raise HTTPException(
        status_code=501,
        detail="Not implemented: get_share in app/main.py",
    )


@app.delete("/api/shares/{token}")
def revoke_share(token: str) -> Dict[str, Any]:
    """
    TODO (candidate):
    - Revoke the share (delete the file OR set revoked=true — pick one, be consistent)
    - 404 if the token does not exist
    - Return {"ok": true}
    """
    raise HTTPException(
        status_code=501,
        detail="Not implemented: revoke_share in app/main.py",
    )
