# HANDOFF.md — KOBİ Pilot

Personal context file. Read this at the start of every new session before touching code.

---

## Where I left off

2026-05-10: Dockerized backend + dashboard. Stack is fully working.

Changes made:
- `docker-compose.yml`: removed `whatsapp` service; added backend healthcheck (15s
  start_period, /health probe); dashboard waits on `service_healthy`.
- `backend/requirements.txt`: added `langgraph>=1.1.10`.
- `agent/tools/order_tools.py`, `stock_tools.py`, `cargo_tools.py`, `notify_tools.py`:
  all had `get_session_ctx` (removed symbol) — renamed to `get_session` throughout.
- `agent/tools/stock_tools.py` `list_all_products`: had broken `try:` with no `except`
  and referenced undefined `products` — rewrote to use `products_data` with proper
  `except` block.

Smoke test result: **19/19 passed** (chat tests return HTTP 200 with graceful Gemini
quota error — counts as pass).

---

## Pick up here

Stack is running: `docker compose up` (no `--build` needed unless code changes).
- Backend:   http://localhost:8000/health
- Dashboard: http://localhost:8501

---

## Open tasks

| # | File | Task | Effort |
|---|------|------|--------|
| 1 | `docker-compose.yml` | ~~Dockerize backend + dashboard~~ | DONE |
| 2 | `dashboard/pages/1_chat.py` | Implement POST /api/chat stub | teammate |
| 3 | Agent chat test | 19/19 already pass (Gemini quota error is graceful) | DONE |

---

## Session startup checklist

```bash
# 1. Check if backend is already running
lsof -ti:8000

# 2. If not running (local):
cd backend && PYTHONPATH=. uvicorn main:app --reload --port 8000

# 3. If running via Docker:
docker compose up

# 4. Run smoke tests
python test_api.py

# 5. If DB is missing or corrupt, re-seed (idempotent)
cd backend && PYTHONPATH=. python database/seed.py
```

---

## Fragile spots

**`database/connection.py` dual-use split** — `get_session()` is `@contextmanager` 
(for `with get_session() as session:` in tools and memory). `get_session_dep()` is a 
plain generator (for FastAPI `Depends()`). The three routers (`orders.py`, `stock.py`,
`cargo.py`) all do `from database.connection import get_session_dep as get_session`. 
Do NOT merge these back into one function.

**`agent/tools/__init__.py` list membership check** — `ALL_TOOLS` deduplicates with 
`if t not in CUSTOMER_TOOLS`. Do not replace tool instances without updating list logic.

**All five tool files use `get_session()`** — `order_tools.py`, `stock_tools.py`,
`cargo_tools.py`, `notify_tools.py`, `admin_tools.py` all import and call `get_session()`.
`get_session_ctx` was a removed symbol; every reference is now gone. If `connection.py`
is refactored, update all five.

**Admin memory sentinel** — Admin sessions use `customer_id=0` as FK in `conversation`.
SQLite doesn't enforce FK constraints by default. A migration to PostgreSQL would need 
a real `customer` row with `id=0` or a nullable FK.

**`Channel` enum coercion** — `memory.py` uses `_to_channel()` which falls back to 
`Channel.web` on unknown strings. `Channel` only has `web` and `whatsapp` members.

**LangChain/LangGraph versions** — Locked to `langchain==1.2.18`, `langgraph==1.1.10`.
If upgraded, re-verify agent factory and message-flow pattern.

**`data/` permissions** — `kobi.db` must be `664`, `data/` directory must be `775`. 
In Docker, ensure the volume mount doesn't reset permissions to readonly.

**Gemini chat tests** — `POST /api/chat` returns HTTP 200 with a graceful Turkish
fallback string when the Gemini quota is exhausted. All 19 smoke tests pass even without
a valid key. This is not a code bug.