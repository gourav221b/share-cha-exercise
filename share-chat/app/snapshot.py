"""
Build a public, read-only snapshot of a chat.

TODO (candidate): implement build_public_snapshot().

Rules of thumb (inspired by our production share flow):
- Keep only human/ai messages (drop role "tool").
- Keep text content.
- If a message has uploaded_files / generated_file_names, keep filenames only —
  strip any url / path fields so the public page never leaks internal URLs.
- Return a dict shaped like:
  {
    "title": "...",
    "messages": [{"role": "human"|"ai", "content": "...", ...optional filename stubs...}],
    "has_artifacts": bool
  }
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_public_snapshot(chat: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a private chat document into a public snapshot.

    Raise NotImplementedError until you implement this.
    """
    # --- implement me ---
    raise NotImplementedError("Implement build_public_snapshot in app/snapshot.py")


def _filename_only(files: Any) -> List[Dict[str, str]]:
    """Helper you may use: keep filename, drop urls."""
    if not isinstance(files, list):
        return []
    out: List[Dict[str, str]] = []
    for item in files:
        if isinstance(item, dict):
            name = (item.get("filename") or "").strip()
            if name:
                out.append({"filename": name})
        elif isinstance(item, str) and item.strip():
            out.append({"filename": item.strip()})
    return out
