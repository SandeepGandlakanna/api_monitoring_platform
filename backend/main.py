from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.database import create_db_and_tables
from backend.routers.monitors import router as monitor_router
from backend.routers.auth import router as auth_router
from backend.services.scheduler_service import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    start_scheduler()
    yield


app = FastAPI(
    title="API Monitoring Platform",
    description="API monitoring and observability backend",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(monitor_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {
        "message": "API Monitoring Platform is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }