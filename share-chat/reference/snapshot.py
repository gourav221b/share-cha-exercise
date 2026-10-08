"""Reference implementation of build_public_snapshot — for reviewers only."""

from __future__ import annotations

from typing import Any, Dict, List


def _filename_only(files: Any) -> List[Dict[str, str]]:
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


def build_public_snapshot(chat: Dict[str, Any]) -> Dict[str, Any]:
    messages_out: List[Dict[str, Any]] = []
    has_artifacts = False

    for msg in chat.get("messages") or []:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        if role == "tool":
            continue
        if role not in ("human", "ai"):
            continue

        entry: Dict[str, Any] = {
            "role": role,
            "content": (msg.get("content") or "").strip(),
        }

        uploads = _filename_only(msg.get("uploaded_files"))
        if uploads:
            entry["uploaded_files"] = uploads
            has_artifacts = True

        generated = _filename_only(msg.get("generated_file_names"))
        if generated:
            entry["generated_file_names"] = generated
            has_artifacts = True

        if entry["content"] or uploads or generated:
            messages_out.append(entry)

    return {
        "title": chat.get("title") or "Shared chat",
        "messages": messages_out,
        "has_artifacts": has_artifacts,
    }
