import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import init_db, engine
from app.routers import orders, logs
from app.ml import vectorizer, model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("order_system")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khoi tao bang du lieu khi ung dung khoi dong
    try:
        init_db()
        logger.info("Khoi tao co so du lieu thanh cong.")
    except Exception as e:
        logger.error(f"Khong the khoi tao database: {e}")
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(orders.router)
app.include_router(logs.router)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.APP_NAME,
        "env": settings.ENVIRONMENT
    })

@app.get("/api/health")
async def health_check():
    db_status = "connected"
    try:
        with engine.connect() as conn:
            pass
    except Exception as e:
        db_status = f"error: {str(e)}"

    ml_status = "ready" if (vectorizer is not None and model is not None) else "fallback_mode"
    llm_provider = "gemini" if settings.GEMINI_API_KEY else ("openai" if settings.OPENAI_API_KEY else "simulation_draft")

    return {
        "status": "ok",
        "database": db_status,
        "ml_model": ml_status,
        "llm_provider": llm_provider,
        "model_name": settings.LLM_MODEL
    }
