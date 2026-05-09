from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.chat import router as chat_router
from api.orders import router as orders_router
from api.stock import router as stock_router
from api.cargo import router as cargo_router
from database.connection import create_db_and_tables
from scheduler.jobs import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    start_scheduler()  # check_critical_stock (15 min interval) · daily_summary (cron 08:00)
    yield
    stop_scheduler()


app = FastAPI(title="KOBİ Pilot API", lifespan=lifespan)

app.include_router(chat_router)
app.include_router(orders_router)
app.include_router(stock_router)
app.include_router(cargo_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
