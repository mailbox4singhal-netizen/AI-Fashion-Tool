"""FastAPI main — SRS §5.2."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import hash_password, require_admin
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.models import User
from app.routes import auth as auth_routes
from app.routes import analyze as analyze_routes
from app.routes import design as design_routes
from app.routes import techpack as techpack_routes
from app.routes import admin as admin_routes
from app.services.llm_client import llm_enabled
from app.utils.logger import log_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # seed demo accounts
    db = SessionLocal()
    try:
        seeds = [
            ("Demo Designer", "demo@fashion.ai",  "demo1234",   "designer"),
            ("Admin",         "admin@fashion.ai", "admin1234",  "admin"),
            ("Demo Shopper",  "shopper@fashion.ai", "shopper1234", "shopper"),
        ]
        for name, email, pw, role in seeds:
            if not db.query(User).filter(User.email == email).first():
                db.add(User(
                    name=name, email=email,
                    password_hash=hash_password(pw), role=role,
                ))
        db.commit()
    finally:
        db.close()

    # Announce LLM config at startup — makes it obvious in logs whether
    # the real model is wired up or we're running on mocks.
    log_event(
        "startup.llm_config",
        provider=settings.llm_provider,
        enabled=llm_enabled(),
        model=(
            settings.anthropic_model if settings.llm_provider == "anthropic"
            else settings.openai_model if settings.llm_provider == "openai"
            else "mock"
        ),
    )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="AI Fashion Intelligence & Design Platform — per SRS/FRS.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(analyze_routes.router)
app.include_router(design_routes.router)
app.include_router(techpack_routes.router)
app.include_router(admin_routes.router)


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "llm": {
            "provider": settings.llm_provider,
            "enabled": llm_enabled(),
        },
        "demo_accounts": {
            "designer": {"email": "demo@fashion.ai",    "password": "demo1234"},
            "shopper":  {"email": "shopper@fashion.ai", "password": "shopper1234"},
            "admin":    {"email": "admin@fashion.ai",   "password": "admin1234"},
        },
    }


@app.get("/health")
def health():
    return {"status": "ok", "llm_enabled": llm_enabled()}


@app.get("/ai-status")
def ai_status(_=Depends(require_admin)):
    """Admin-only: verify the configured LLM provider + model is reachable."""
    from app.services.llm_client import get_llm_client

    info = {
        "provider":   settings.llm_provider,
        "enabled":    llm_enabled(),
        "model":
            settings.anthropic_model if settings.llm_provider == "anthropic"
            else settings.openai_model if settings.llm_provider == "openai"
            else None,
    }
    if not llm_enabled():
        info["message"] = (
            "No real LLM configured — running in MOCK mode. "
            "Set LLM_PROVIDER and the matching API key in .env to enable."
        )
    else:
        try:
            get_llm_client()  # instantiates the SDK client
            info["message"] = "Client initialised successfully."
        except Exception as e:
            info["error"] = str(e)
    return info
