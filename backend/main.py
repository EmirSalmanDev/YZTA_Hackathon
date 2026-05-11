# ---------------------------------------------------------------------------
# IPv4 zorlaması — macOS'ta IPv6 DNS çözümlemesi Google API'ye bağlanamıyor.
# Bu patch tüm socket çağrılarını IPv4'e zorlar.
# ---------------------------------------------------------------------------
import socket

_original_getaddrinfo = socket.getaddrinfo


def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = _ipv4_only_getaddrinfo
# ---------------------------------------------------------------------------

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlmodel import Session, select

from api.cargo import router as cargo_router
from api.chat import router as chat_router
from api.orders import router as orders_router
from api.stock import router as stock_router
from database.connection import create_db_and_tables, engine
from database.models import CargoEvent, Conversation, Customer, Order, Product
from database.seed import seed
from scheduler.jobs import start_scheduler, stop_scheduler

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed()                  # no-op if already seeded
    start_scheduler()       # check_critical_stock (15 min) · daily_summary (08:00)
    yield
    stop_scheduler()


app = FastAPI(title="KOBİ Pilot API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",     # Streamlit dashboard (local)
        "http://localhost:8502",     # WhatsApp bot (local)
        "http://dashboard:8501",    # Streamlit dashboard (Docker)
        "http://telegram:8502",     # Telegram bot (Docker)
        "*",                        # Fallback — tüm origin'ler
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(chat_router,   tags=["chat"])
app.include_router(orders_router, tags=["orders"])
app.include_router(stock_router,  tags=["stock"])
app.include_router(cargo_router,  tags=["cargo"])


@app.get("/health", tags=["meta"])
async def health() -> dict:
    with Session(engine) as session:
        db_counts = {
            "customers":     session.exec(select(func.count()).select_from(Customer)).one(),
            "products":      session.exec(select(func.count()).select_from(Product)).one(),
            "orders":        session.exec(select(func.count()).select_from(Order)).one(),
            "cargo_events":  session.exec(select(func.count()).select_from(CargoEvent)).one(),
            "conversations": session.exec(select(func.count()).select_from(Conversation)).one(),
        }
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
        "db": db_counts,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
