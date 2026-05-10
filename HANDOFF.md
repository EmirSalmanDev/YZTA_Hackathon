# HANDOFF.md — KOBİ Pilot

Personal context file. Read this at the start of every new session before touching code.

---

## Where I left off

A full debugging session on 2026-05-09 fixed every startup-blocking bug in the backend. The backend boots cleanly, all 16 non-chat smoke tests pass (19/19 when `GOOGLE_API_KEY` is set). The agent reaches Gemini correctly but hit a free-tier 429 at test time — no code change needed, it will work once quota resets or a paid key is used.

The session ended after updating `CLAUDE.md` and creating this file.

---

## Pick up here

The three open bugs (priority order):

1. **`dashboard/pages/3_stock.py` line 20** — `p["sku"]` → `p["name"]`, rename `critical_skus` → `critical_names`.
2. **`dashboard/pages/1_chat.py`** — Replace the `"..."` stub with an actual `POST /api/chat` call. The backend endpoint is `POST /api/chat` with body `{message: str, customer_id: int, channel: str}`. Response field is `response` (not `reply`).
3. **`agent/tools/admin_tools.py` orphaned** — Add imports for `get_business_stats`, `search_customer`, `get_pending_orders` to `backend/agent/tools/__init__.py` and append them to `ADMIN_TOOLS`.

After those three, verify the agent returns real Turkish replies by running `python test_api.py` with a valid `GOOGLE_API_KEY` in `.env`.

---

## Open tasks (priority-ordered)

| # | File | Task | Effort |
|---|------|------|--------|
| 1 | `dashboard/pages/3_stock.py:20` | `p["sku"]` → `p["name"]`, rename `critical_skus` | 2 min |
| 2 | `dashboard/pages/1_chat.py` | Implement chat submit → `POST /api/chat` | 15 min |
| 3 | `backend/agent/tools/__init__.py` | Import + add `admin_tools.py` tools to `ADMIN_TOOLS` | 5 min |
| 4 | Gemini quota | Verify real Turkish reply once quota resets / paid key | test only |

---

## Fragile spots

**`database/connection.py` dual-use split** — `get_session()` is `@contextmanager` (for `with get_session() as session:` in tools and memory). `get_session_dep()` is a plain generator (for FastAPI `Depends()`). The three routers (`orders.py`, `stock.py`, `cargo.py`) all do `from database.connection import get_session_dep as get_session`. Do NOT merge these back into one function — FastAPI's `Depends()` calls `next()` directly and will break if the function is decorated with `@contextmanager`.

**`agent/tools/__init__.py` list membership check** — `ALL_TOOLS` deduplicates with `if t not in CUSTOMER_TOOLS`. This works because `@tool`-decorated functions are singletons (same object). Do not replace them with new instances (e.g., re-importing after reload) without updating the list logic.

**Admin memory sentinel** — Admin sessions use `customer_id=0` as the FK in `conversation`. SQLite doesn't enforce FK constraints by default, so this writes cleanly. A migration to a proper DB (PostgreSQL) would need a real `customer` row with `id=0` or a nullable FK.

**`Channel` enum coercion** — `memory.py` uses `_to_channel()` which falls back to `Channel.web` on unknown strings (e.g., `"dashboard"`). Admin channel is stored as `Channel.web`, not `"dashboard"`. This is intentional — `Channel` only has `web` and `whatsapp` members.

**LangChain/LangGraph versions** — Locked to `langchain==1.2.18`, `langgraph==1.1.10`. The orchestrator uses `langgraph.prebuilt.create_react_agent` (not `langchain.agents`). If dependencies are upgraded, re-verify the agent factory and message-flow pattern.

---

## Session startup checklist

```bash
# 1. Check if backend is already running
lsof -ti:8000

# 2. If not running, start it (from repo root)
cd backend && PYTHONPATH=. uvicorn main:app --reload --port 8000

# 3. Run smoke tests (separate terminal, from repo root)
python test_api.py

# 4. For chat tests to run, .env must have GOOGLE_API_KEY set
#    Check: grep GOOGLE_API_KEY .env

# 5. If DB is missing or corrupt, re-seed (idempotent)
cd backend && PYTHONPATH=. python database/seed.py
```

If uvicorn fails to start, the most common causes are:
- Port 8000 in use: `lsof -ti:8000 | xargs kill -9`
- Missing `.env`: copy from a teammate or create with at least `GOOGLE_API_KEY=`
- Missing packages: `pip install -r backend/requirements.txt`
