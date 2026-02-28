from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, SessionLocal, Base
from app.api import draws, predictions, status, simulation
from app import models  # noqa: F401  # Ensure all ORM models are registered before create_all
from scheduler.tasks import setup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + start scheduler
    Base.metadata.create_all(bind=engine)
    scheduler = setup_scheduler(SessionLocal)
    app.state.scheduler = scheduler
    yield
    # Shutdown: stop scheduler
    app.state.scheduler.shutdown()


app = FastAPI(
    title="BINGO BINGO 分析 API",
    description="台灣彩券 BINGO BINGO 號碼分析",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(draws.router, prefix="/api/draws", tags=["開獎資料"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["預測"])
app.include_router(status.router, prefix="/api/status", tags=["狀態"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["模擬投注"])


@app.get("/")
def root():
    return {"message": "BINGO 分析 API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
