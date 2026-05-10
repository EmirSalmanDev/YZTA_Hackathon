# KOBİ Pilot — Developer README

## Project Overview

KOBİ Pilot is a Turkish SME (Küçük ve Orta Büyüklükteki İşletme) management platform. It gives small business owners a chat-driven interface to query orders, monitor stock levels, and track cargo shipments. An AI agent (LangChain + Gemini) handles natural-language requests from both customers and the business owner.

**Tech stack**

| Layer | Technology |
|-------|-----------|
| API backend | FastAPI 0.111+, Python 3.11 |
| ORM / DB | SQLModel + SQLite (`data/kobi.db`) |
| AI agent | LangChain 0.2+, LangGraph 1.1+, Google Gemini (`langchain-google-genai`) |
| Scheduler | APScheduler 3.10+ |
| Dashboard | Streamlit 1.35+ |
| Containers | Docker Compose (backend + dashboard) |

**Architecture**

```
Browser
  │
  ▼
Dashboard (Streamlit :8501)
  │  HTTP (requests)
  ▼
Backend API (FastAPI :8000)
  ├── /orders  ──────────────────────────────┐
  ├── /stock   ──────────────────────────────┤
  ├── /cargo   ──────────────────────────────┤  SQLModel
  └── /api/chat ──► agent/orchestrator.py    │  ────────► data/kobi.db (SQLite)
                        │                    │
                        ▼                    │
                    agent/tools/*.py ────────┘
                        │
                        ▼
                    Google Gemini API
```

---

## Prerequisites

- **Docker Desktop** (for the containerised quick-start)
- **Python 3.11+** (for local development without Docker)
- **`GOOGLE_API_KEY`** — a Google AI Studio / Gemini API key (required for the chat agent; without it, chat endpoints return a graceful Turkish fallback message with HTTP 200)

---

## Quick Start (Docker)

```bash
# 1. Copy the example env file and add your Gemini key
cp .env.example .env          # or create .env manually (see Environment Variables below)

# 2. Build images and start services
docker compose up --build -d

# 3. Verify the backend is healthy
curl http://localhost:8000/health

# 4. Open the dashboard
open http://localhost:8501     # macOS — or visit in browser
```

On subsequent runs (no code changes) you can skip `--build`:

```bash
docker compose up -d
```

---

## Running Locally (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
PYTHONPATH=. python database/seed.py   # creates/seeds data/kobi.db (idempotent)
PYTHONPATH=. uvicorn main:app --reload --port 8000

# Dashboard (separate terminal)
cd dashboard
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

Run the smoke-test suite (expects 19/19):

```bash
python test_api.py
```

Re-seed the database at any time (safe to run repeatedly):

```bash
cd backend && PYTHONPATH=. python database/seed.py
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | **Yes** (for agent) | Google AI Studio key for Gemini. Without it, `/api/chat` returns an HTTP 200 with a quota/error message. |
| `TWILIO_ACCOUNT_SID` | No (whatsapp scope) | Twilio credentials — used by the `whatsapp/` service which is excluded from this stack. |
| `TWILIO_AUTH_TOKEN` | No (whatsapp scope) | See above. |
| `TWILIO_WHATSAPP_NUMBER` | No (whatsapp scope) | See above. |

Place all variables in a `.env` file at the project root. Both Docker services load it via `env_file: .env` in `docker-compose.yml`.

---

## API Reference

All endpoints are served from `http://localhost:8000`.

### Meta

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check. Returns `{"status":"ok","time":"…","db":{…}}` with row counts for all tables. |

### Chat — `/api/chat`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Customer chat. Requires `{"message":"…","customer_id":1,"channel":"web"}`. Returns `{"response":"…","customer_id":1,"channel":"web","timestamp":"…","status":"ok"}`. |
| `POST` | `/api/chat/admin` | Admin/owner chat. Requires `{"message":"…"}`. Has access to extended tools (stats, pending orders, customer search). |
| `GET` | `/api/chat/history/{customer_id}` | Conversation history for a customer. Optional `?channel=web`. |
| `DELETE` | `/api/chat/history/{customer_id}` | Clear conversation memory for a customer. Optional `?channel=web`. |
| `GET` | `/api/chat/health` | Agent health check — confirms the orchestrator is initializable. |

**Customer chat example**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Siparişim nerede?","customer_id":1,"channel":"web"}'
```

### Orders — `/orders`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/orders` | List all orders. Optional query params: `?status=pending\|shipped\|delivered\|cancelled` and `?filter_date=YYYY-MM-DD`. |
| `GET` | `/orders/{id}` | Fetch a single order by ID. |
| `PATCH` | `/orders/{id}/status` | Update order status. Body: `{"status":"shipped"}`. Valid values: `pending`, `shipped`, `delivered`, `cancelled`. |

### Stock — `/stock`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/stock` | List all products with current stock levels. |
| `GET` | `/stock/critical` | Products where `stock_amount <= critical_threshold`. |
| `PATCH` | `/stock/{id}` | Update stock amount. Body: `{"stock_amount":42}`. Must be ≥ 0. |

### Cargo — `/cargo`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/cargo/track/{tracking_id}` | Mock cargo status for a tracking ID. Returns carrier, status, location, and estimated delivery. |
| `GET` | `/cargo/delays` | All orders with a `cargo_tracking_id` whose mock status is `"Gecikmiş"` (delayed). |

---

## Project Structure

```
YZTA_Hackathon/
├── .env                        # real secrets — gitignored
├── docker-compose.yml          # backend + dashboard services
├── test_api.py                 # smoke tests (19 checks)
│
├── data/
│   ├── kobi.db                 # SQLite database (volume-mounted in Docker)
│   ├── alerts.json             # written by scheduler stock-alert job
│   └── daily_summary.json      # written by scheduler daily-summary job
│
├── backend/
│   ├── main.py                 # FastAPI app, CORS, lifespan (seed + scheduler)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── database/
│   │   ├── connection.py       # engine, get_session() (contextmanager), get_session_dep() (FastAPI Depends)
│   │   ├── models.py           # Customer, Product, Order, CargoEvent, Conversation (SQLModel)
│   │   └── seed.py             # Faker-based seed — idempotent
│   ├── api/
│   │   ├── chat.py             # POST /api/chat, POST /api/chat/admin, GET+DELETE /api/chat/history/{id}
│   │   ├── orders.py           # GET /orders, GET /orders/{id}, PATCH /orders/{id}/status
│   │   ├── stock.py            # GET /stock, GET /stock/critical, PATCH /stock/{id}
│   │   └── cargo.py            # GET /cargo/track/{id}, GET /cargo/delays
│   ├── agent/
│   │   ├── orchestrator.py     # KobiAgentOrchestrator (LangGraph create_react_agent)
│   │   ├── memory.py           # Per-customer conversation memory (Channel enum coercion)
│   │   └── tools/
│   │       ├── __init__.py     # Exports CUSTOMER_TOOLS, ADMIN_TOOLS, ALL_TOOLS
│   │       ├── order_tools.py
│   │       ├── stock_tools.py
│   │       ├── cargo_tools.py
│   │       ├── notify_tools.py
│   │       └── admin_tools.py  # get_business_stats, search_customer, get_pending_orders
│   ├── scheduler/
│   │   └── jobs.py             # APScheduler: stock check every 15 min, daily summary at 08:00
│   └── mock/
│       └── cargo_mock.py       # Deterministic mock cargo responses (no real carrier API)
│
├── dashboard/
│   ├── app.py                  # Streamlit entry point + sidebar navigation
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pages/
│       ├── 1_chat.py           # Customer chat UI — stub (under development)
│       ├── 2_orders.py         # Orders list + status PATCH
│       ├── 3_stock.py          # Stock list with critical-stock highlight
│       └── 4_cargo.py          # Cargo tracking page
│
└── whatsapp/                   # Separate teammate scope — NOT in docker-compose.yml
```

---

## Services & Ports

| Service | Port | URL |
|---------|------|-----|
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| Dashboard (Streamlit) | 8501 | http://localhost:8501 |
| FastAPI interactive docs | 8000 | http://localhost:8000/docs |
| FastAPI ReDoc | 8000 | http://localhost:8000/redoc |

In Docker Compose, the dashboard waits for the backend's `/health` probe to return healthy before starting (`depends_on: condition: service_healthy`).

---

## Database

**Engine:** SQLite, stored at `data/kobi.db`.

**Tables** (defined in `backend/database/models.py`):

| Table | Description |
|-------|-------------|
| `customer` | Customers: name, phone, email, WhatsApp number |
| `product` | Products: name, stock amount, critical threshold, unit, price |
| `orders` | Orders: customer FK, status, total price, created_at, delivery date, cargo tracking ID |
| `cargoevent` | Cargo events: order FK, status, location, timestamp |
| `conversation` | Conversation records: customer FK, channel (web/whatsapp), last message, updated_at |

**Admin sessions** use `customer_id=0` as a sentinel in `conversation`. SQLite doesn't enforce FK constraints by default; a migration to PostgreSQL would need a matching `customer` row or a nullable FK.

**Re-seed (idempotent):**

```bash
cd backend && PYTHONPATH=. python database/seed.py
```

**Docker volume:** `./data` is mounted to `/app/data` inside the backend container. Ensure `data/kobi.db` has permissions `664` and `data/` has `775` to avoid read-only errors:

```bash
chmod 664 data/kobi.db
chmod 775 data/
```

---

## Known Limitations

- **Gemini free-tier quota.** When the Gemini API quota is exhausted or `GOOGLE_API_KEY` is missing, `/api/chat` and `/api/chat/admin` return HTTP 200 with a Turkish fallback message instead of an AI reply. All 19 smoke tests pass in this state — it is not a code bug.
- **WhatsApp service excluded.** The `whatsapp/` directory exists in the repository but is not included in `docker-compose.yml`. It is a separate teammate's scope and has no integration with the current Docker stack.
- **SQLite only.** The current setup uses SQLite. A migration to PostgreSQL would require adding a real `customer` row with `id=0` (or a nullable FK) for the admin-session sentinel, and enabling FK constraint enforcement.
- **LangChain/LangGraph versions are pinned.** Locked to `langchain==0.2.x` / `langchain-google-genai>=1.0.6` / `langgraph>=1.1.10`. Upgrading requires re-verifying the agent factory and message-flow pattern in `agent/orchestrator.py`.
