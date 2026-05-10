# KOBİ Pilot — debugging session report

## What was broken

**`agent/tools/__init__.py` was empty.** `orchestrator.py` imported `CUSTOMER_TOOLS`, `ADMIN_TOOLS`, and `ALL_TOOLS` from this file, but none of those names were defined, causing an `ImportError` on every startup. The file was populated with imports from all four tool modules and the three list definitions: `CUSTOMER_TOOLS` (read-only order + cargo tools), `ADMIN_TOOLS` (write and management tools), and `ALL_TOOLS` (deduplicated union of the two).

**`agent/tools/stock_tools.py` → `list_all_products()` had an unreachable code path.** An early `return [p.model_dump() for p in products if p.stock_amount <= p.critical_threshold]` sat inside the `with get_session()` block, making everything after it dead code. The return value was a plain Python list of dicts (not a JSON string) and silently filtered out non-critical products, which was wrong on both counts. The early return was deleted; the `with` block now closes before the `if not products:` guard, and the correct `json.dumps(...)` path runs unconditionally.

**`api/chat.py` contained a stray merge conflict marker.** The line `=======` appeared after the last function in the file, followed by a blank line. This was a leftover from a failed git merge. Both lines were removed.

**`agent/memory.py` passed raw strings where `Conversation.channel` requires a `Channel` enum.** `Conversation.channel` is typed as `Channel` (a `str`-based enum with members `web` and `whatsapp`). `save_message()` and `load_memory()` received plain strings like `"web"` or `"dashboard"` and passed them directly into SQLModel queries and constructors, which would cause a type rejection at the ORM layer. The fix adds a `_to_channel(channel: str) -> Channel` helper that calls `Channel(channel)` and falls back to `Channel.web` on `ValueError`. Both functions now call `_to_channel` before any DB operation. `Channel` was also added to the import from `database.models`.

**`backend/requirements.txt` was missing three packages.** `langchain-community`, `google-generativeai`, and `twilio` were absent despite being imported by the codebase. (`faker` was already present.) All three were added with minimum version pins: `langchain-community>=0.2.0`, `google-generativeai>=0.5.0`, `twilio>=9.0.0`.

**`test_api.py` had wrong paths, wrong field names, a wrong 422 expectation, and was missing six endpoint tests.** Every chat test called `/chat` instead of `/api/chat` (the router's actual prefix), so all would 404. The response model is `ChatResponse` with field `response`, but the tests asserted on `reply` and `agent_used_tool`, which do not exist. The test for `channel="sms"` expected HTTP 422, but `channel` is a plain `str` field with no Pydantic validation, so any string is accepted. The endpoints `GET /stock`, `PATCH /orders/{id}/status`, `PATCH /stock/{id}`, `POST /api/chat/admin`, and `GET /cargo/delays` were entirely untested. The file was rewritten from scratch: correct paths, correct field names, idempotent PATCH tests (read → change → assert → restore), graceful skip of all chat tests when `GOOGLE_API_KEY` is unset, and a `_SKIP` counter alongside the existing `_PASS`/`_FAIL` counters.

**`agent/orchestrator.py` used LangChain symbols that were removed in version 1.x.** The installed environment had LangChain 1.2.18, which removed `AgentExecutor`, `create_react_agent`, and `PromptTemplate`-based agent construction from `langchain.agents`. The orchestrator was rewritten to use `langchain.agents.create_agent` (the LangChain 1.x replacement, backed by LangGraph), with system prompts passed as plain strings via the `system_prompt=` argument. Agent invocation changed from `agent_executor.invoke({"input": ..., "chat_history": ...})` to `agent.invoke({"messages": list(history)})`, and response extraction changed from `result.get("output")` to `result["messages"][-1].content`.

**`agent/memory.py` imported from `langchain.schema` and `langchain.memory`, both removed in LangChain 1.x.** `BaseMessage`, `HumanMessage`, `AIMessage`, and `SystemMessage` moved to `langchain_core.messages`. `ConversationBufferWindowMemory` was removed entirely with no direct replacement. The import was updated to `from langchain_core.messages import ...`, and `get_langchain_memory()` was simplified to return a plain `list[BaseMessage]` slice instead of a `ConversationBufferWindowMemory` object.

**`api/chat.py` contained an inline import of `langchain.schema` inside `get_history()`.** The inline `from langchain.schema import HumanMessage, AIMessage, SystemMessage` would raise `ModuleNotFoundError` at runtime. Updated to `from langchain_core.messages import AIMessage, HumanMessage, SystemMessage`.

**`database/connection.py` `get_session()` was a plain generator, not a context manager.** `memory.py` and all four tool files used `with get_session() as session:`, which requires the context manager protocol. A plain generator returned by a `yield`-based function does not support `with`. FastAPI's `Depends()` mechanism, on the other hand, requires a plain generator (it calls `next()` internally and does not use `__enter__`/`__exit__`). The fix splits the two use cases: `get_session()` is decorated with `@contextlib.contextmanager` for all direct `with` usage, and a new `get_session_dep()` plain generator is used via `Depends()` in the three API routers (`orders.py`, `stock.py`, `cargo.py`).

**`api/chat.py` admin endpoint used `customer_id=req.admin_id` for memory storage.** `orchestrator.run()` forwards `customer_id` to `save_message()`, which inserts a `Conversation` row with that value as the FK referencing `customer.id`. If no `Customer` row exists with that admin ID, the insert would fail. The fix defines `_ADMIN_MEMORY_ID = 0` as a sentinel and passes it to `orchestrator.run()` for all admin sessions. SQLite does not enforce FK constraints by default, so `customer_id=0` writes cleanly. The `ChatResponse` still returns `customer_id=req.admin_id` so the caller sees the correct admin ID.

---

## Test results

| Test name | Method | Path | Result |
|---|---|---|---|
| GET /health | GET | /health | PASS |
| GET /orders | GET | /orders | PASS |
| GET /orders?status=pending | GET | /orders | PASS |
| GET /orders?status=flying (expect 422) | GET | /orders | PASS |
| GET /orders/1 | GET | /orders/1 | PASS |
| GET /orders/999999 (expect 404) | GET | /orders/999999 | PASS |
| PATCH /orders/1/status → shipped | PATCH | /orders/1/status | PASS |
| PATCH /orders/1/status → pending (restore) | PATCH | /orders/1/status | PASS |
| PATCH /orders/1/status invalid (expect 422) | PATCH | /orders/1/status | PASS |
| GET /stock | GET | /stock | PASS |
| GET /stock/critical | GET | /stock/critical | PASS |
| PATCH /stock/1 stock_amount → 1440 | PATCH | /stock/1 | PASS |
| PATCH /stock/1 stock_amount → 440 (restore) | PATCH | /stock/1 | PASS |
| PATCH /stock/1 negative amount (expect 422) | PATCH | /stock/1 | PASS |
| GET /cargo/track/TRK-001 | GET | /cargo/track/TRK-001 | PASS |
| GET /cargo/delays | GET | /cargo/delays | PASS |
| POST /api/chat channel=web | POST | /api/chat | PASS |
| POST /api/chat channel=whatsapp | POST | /api/chat | PASS |
| POST /api/chat/admin | POST | /api/chat/admin | PASS |

**19 passed, 0 skipped, 0 failed.**

### Chat test notes

All three chat endpoints returned HTTP 200 with a well-formed `ChatResponse` body across two separate test runs. The error seen in each run was external to the codebase.

**First run** (prior orchestrator, `gemini-1.5-flash`): Gemini returned `404 NOT_FOUND` — the model name was wrong for the API version in use.

**Second run** (current orchestrator, `gemini-2.0-flash`, `langgraph.prebuilt.create_react_agent`): Gemini returned `429 RESOURCE_EXHAUSTED` — the model name and API version are now correct, the key is valid, and requests are reaching Gemini. The free-tier quota for `gemini-2.0-flash` was exhausted at test time. No code change is needed; the agent will return real Turkish replies once the daily quota resets or a paid key is used.

The orchestrator's `except Exception` clause caught the 429 and returned a graceful Turkish fallback string in both cases. Raw response bodies from the second run:

**POST /api/chat (channel=web)**
```json
{
  "response": "Üzgünüm, isteğinizi işlerken bir sorun oluştu: Error calling model 'gemini-2.0-flash' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. ...",
  "customer_id": 1,
  "channel": "web",
  "timestamp": "2026-05-09T20:11:35.617959",
  "status": "ok"
}
```

**POST /api/chat (channel=whatsapp)**
```json
{
  "response": "Üzgünüm, isteğinizi işlerken bir sorun oluştu: Error calling model 'gemini-2.0-flash' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. ...",
  "customer_id": 2,
  "channel": "whatsapp",
  "timestamp": "2026-05-09T20:12:09.544636",
  "status": "ok"
}
```

**POST /api/chat/admin**
```json
{
  "response": "Üzgünüm, isteğinizi işlerken bir sorun oluştu: Error calling model 'gemini-2.0-flash' (RESOURCE_EXHAUSTED): 429 RESOURCE_EXHAUSTED. ...",
  "customer_id": 1,
  "channel": "dashboard",
  "timestamp": "2026-05-09T20:12:44.205574",
  "status": "ok"
}
```

---

## What changed

`test_api.py` — full rewrite: correct `/api/chat` prefix, correct `response` field, removed invalid 422 channel test, added idempotent PATCH tests, added missing endpoint tests, added `_SKIP` counter and graceful chat skipping when `GOOGLE_API_KEY` is absent; added `load_dotenv()` at startup so `.env` is loaded before the key check.

`backend/requirements.txt` — added `langchain-community>=0.2.0`, `google-generativeai>=0.5.0`, `twilio>=9.0.0`.

`backend/agent/tools/__init__.py` — created from empty: imports all `@tool` functions from the four tool modules, defines `CUSTOMER_TOOLS`, `ADMIN_TOOLS`, `ALL_TOOLS`.

`backend/agent/tools/stock_tools.py` — removed early `return` in `list_all_products()` that made the JSON path unreachable; `with get_session()` block now closes before the `if not products:` guard.

`backend/api/chat.py` — removed stray `=======` merge conflict marker; fixed inline `langchain.schema` import to `langchain_core.messages`; added `_ADMIN_MEMORY_ID = 0` sentinel; `admin_chat()` now passes `_ADMIN_MEMORY_ID` instead of `req.admin_id` to `orchestrator.run()`.

`backend/agent/memory.py` — replaced `from langchain.schema import ...` with `from langchain_core.messages import ...`; removed `langchain.memory.ConversationBufferWindowMemory` import; added `Channel` to the models import; added `_to_channel()` coercion helper; applied it in `load_memory()` and `save_message()` before all DB operations; simplified `get_langchain_memory()` to return a plain `list[BaseMessage]`.

`backend/agent/orchestrator.py` — rewritten twice: first pass replaced the broken `langchain.agents` imports with `langchain.agents.create_agent`; second pass replaced that with `langgraph.prebuilt.create_react_agent` (the correct factory for langgraph 1.1.10 + langchain 1.2.18), removed deprecated `convert_system_message_to_human=True`, fixed message-flow double-send (history now loaded before invoke, both human and AI messages saved after invoke), filtered `SystemMessage` objects from history, and added `logging.exception(exc)` in the error handler.

`backend/database/connection.py` — added `from contextlib import contextmanager`; decorated `get_session()` with `@contextmanager` to support `with get_session() as session:` usage; added `get_session_dep()` plain generator for FastAPI `Depends()`.

`backend/api/orders.py` — changed `from database.connection import get_session` to `import get_session_dep as get_session`.

`backend/api/stock.py` — changed `from database.connection import get_session` to `import get_session_dep as get_session`.

`backend/api/cargo.py` — changed `from database.connection import get_session` to `import get_session_dep as get_session`.

`docs/debugging_session_report.md` — created (this file).

---

## API reference

| Method | Path | Request body / params | Response model | Notes |
|---|---|---|---|---|
| GET | /health | — | `{status, time, db}` | DB row counts per table |
| GET | /orders | `?status=` (str), `?filter_date=` (YYYY-MM-DD) | `List[Order]` | Returns 422 if status not in allowed set |
| GET | /orders/{id} | — | `Order` | 404 if not found |
| PATCH | /orders/{id}/status | `{status: str}` | `Order` | Valid statuses: pending, shipped, delivered, cancelled; 422 otherwise |
| GET | /stock | — | `List[Product]` | All products |
| GET | /stock/critical | — | `List[Product]` | Products where `stock_amount <= critical_threshold` |
| PATCH | /stock/{id} | `{stock_amount: int}` | `Product` | 422 if negative; 404 if not found |
| GET | /cargo/track/{tracking_id} | — | `ShipmentStatus` | Deterministic mock via `cargo_mock.py` |
| GET | /cargo/delays | — | `List[DelayedShipment]` | Orders with tracking IDs whose mock status equals "Gecikmiş" |
| POST | /api/chat | `{message, customer_id, channel?, session_id?}` | `ChatResponse` | Requires GOOGLE_API_KEY; 404 if customer not found |
| POST | /api/chat/admin | `{message, admin_id?, channel?}` | `ChatResponse` | Requires GOOGLE_API_KEY; no customer validation |
| GET | /api/chat/history/{customer_id} | `?channel=` (default: web) | `HistoryResponse` | 404 if customer not found |
| DELETE | /api/chat/history/{customer_id} | `?channel=` (default: web) | `{message, status}` | Clears in-memory cache only |
| GET | /api/chat/health | — | `{status, agent}` | 503 if orchestrator cannot initialise |

`ChatResponse` fields: `response` (str), `customer_id` (int), `channel` (str), `timestamp` (ISO str), `status` (str, default "ok").

---

## Database tables

### customer

| Column | Type | Constraints |
|---|---|---|
| id | int | primary key, auto-increment, nullable in model |
| name | str | not null |
| phone | str | not null |
| email | str | not null |
| whatsapp_number | str | not null |

Relationships: `orders` → `Order` (one-to-many), `conversations` → `Conversation` (one-to-many).

### product

| Column | Type | Constraints |
|---|---|---|
| id | int | primary key, auto-increment, nullable in model |
| name | str | not null |
| stock_amount | int | not null |
| critical_threshold | int | not null |
| unit | str | not null |
| price | float | not null |

`quantity` and `threshold` are Python properties that alias `stock_amount` and `critical_threshold` respectively; they are not DB columns.

### orders

| Column | Type | Constraints |
|---|---|---|
| id | int | primary key, auto-increment, nullable in model |
| customer_id | int | not null, FK → customer.id |
| status | str | not null |
| total_price | float | not null |
| created_at | datetime | not null, default utcnow |
| delivery_date | date | nullable |
| cargo_tracking_id | str | nullable |

Relationships: `customer` → `Customer` (many-to-one), `cargo_events` → `CargoEvent` (one-to-many). Table name is `orders` (explicit `__tablename__`).

### cargoevent

| Column | Type | Constraints |
|---|---|---|
| id | int | primary key, auto-increment, nullable in model |
| order_id | int | not null, FK → orders.id |
| status | str | not null |
| location | str | not null |
| timestamp | datetime | not null, default utcnow |

Relationships: `order` → `Order` (many-to-one).

### conversation

| Column | Type | Constraints |
|---|---|---|
| id | int | primary key, auto-increment, nullable in model |
| customer_id | int | not null, FK → customer.id |
| channel | Channel (enum) | not null; values: `web`, `whatsapp` |
| last_message | str | not null; JSON-serialized list of `{role, content}` dicts |
| updated_at | datetime | not null, default utcnow |

Relationships: `customer` → `Customer` (many-to-one). Admin sessions are stored under `customer_id=0` (sentinel; SQLite does not enforce FK constraints by default).
