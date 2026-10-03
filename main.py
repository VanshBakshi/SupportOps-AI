from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.connection import init_db
from app.api import tickets, analytics, health, auth

@asynccontextmanager
async def lifespan(app:FastAPI):
    setup_logging(); init_db(); logger.info("SupportOps AI started")
    yield
    logger.info("SupportOps AI stopped")

app=FastAPI(title=settings.app_name,version="1.0.0",description="AI-powered support ticket operations platform",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(health.router,prefix="/api/v1")
app.include_router(auth.router,prefix="/api/v1")
app.include_router(tickets.router,prefix="/api/v1")
app.include_router(analytics.router,prefix="/api/v1")

@app.get("/")
def root(): return {"name":settings.app_name,"version":"1.0.0","docs":"/docs","dashboard":"/dashboard"}

DASH=Path(__file__).resolve().parents[2]/"frontend"/"dashboard.html"
@app.get("/dashboard",include_in_schema=False)
def dashboard():
    from fastapi.responses import FileResponse
    return FileResponse(DASH)
