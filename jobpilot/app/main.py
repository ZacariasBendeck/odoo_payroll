from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import create_tables

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="JobPilot",
    description="AI-powered Job Assistant",
    version="0.1.0",
    lifespan=lifespan,
)

# Static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# API routers
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.team import router as team_router
from app.api.ai import router as ai_router
from app.api.email import router as email_router
from app.api.whatsapp import router as whatsapp_router

app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(team_router)
app.include_router(ai_router)
app.include_router(email_router)
app.include_router(whatsapp_router)

# Web pages
from app.web.pages import router as pages_router

app.include_router(pages_router)
