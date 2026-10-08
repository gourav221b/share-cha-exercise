# Share Chat — Fullstack take-home

Build a **public share-link** feature for chat conversations.

This is a simplified, file-backed version of a pattern we use in production: create a read-only snapshot, expose it via a token URL, and allow revoke. You do **not** need Docker, a database, Redis, or Node.

**Timebox:** ~2–3 hours. Stretch goals are optional.

---

## Setup (should take under 2 minutes)

Requires Python 3.10+.

```bash
cd share-chat-takehome
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8765
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

Seed chats live in `data/chats.json`. Your shares should be written as JSON files under `data/shares/`.

---

## What is already done

| Piece | Status |
|-------|--------|
| Seed chats + file helpers (`app/store.py`) | Done — use these |
| List/get chat APIs | Done |
| Static HTML/JS UI | Done — it calls your APIs |
| `POST /api/shares` | **You implement** |
| `GET /api/shares/{token}` | **You implement** |
| `DELETE /api/shares/{token}` | **You implement** |
| `build_public_snapshot()` | **You implement** |

---

## Acceptance criteria

1. **Create share** — `POST /api/shares` with `{ "chat_id": "..." }`  
   - 404 if chat missing  
   - Persists a share file under `data/shares/`  
   - Returns `{ "token", "url", "title", "expires_at" }` (`expires_at` may be `null` if you skip TTL)

2. **Public read** — `GET /api/shares/{token}`  
   - Returns title + snapshot messages  
   - 404 if missing, revoked, or expired  
   - Must **not** expose internal file URLs from the seed data

3. **Revoke** — `DELETE /api/shares/{token}`  
   - Share becomes unavailable on subsequent GET  
   - 404 if token unknown

4. **Snapshot rules**  
   - Drop `tool` messages  
   - Keep `human` / `ai` text  
   - For `uploaded_files` / `generated_file_names`, keep **filenames only** (strip `url`)  
   - Set `has_artifacts: true` when any filenames were present

5. **UI works end-to-end** — Create → open public page → revoke → public page fails

---

## Stretch (nice to have, not required)

- Honor `ttl_days` on create; reject expired shares on GET  
- Re-sharing the same chat returns the **same** active token (stable links)  
- Basic rate limit on create (e.g. N per minute per process)  
- A couple of pytest cases for snapshot stripping / expiry

---

## What to send back

- Your branch / zip of the project  
- A short note (5–10 lines): design choices, tradeoffs, what you’d do next with more time  
- How you verified (manual steps or tests)

---

## Notes / constraints

- Prefer the helpers in `app/store.py` over inventing a new storage layer  
- No auth is required for this exercise (pretend the owner UI is already authenticated)  
- Keep dependencies minimal — stick to what’s in `requirements.txt` unless you have a strong reason
