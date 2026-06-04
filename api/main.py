import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router
from ingestion.logger import get_logger

logger = get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: warm up embedding model only.
    # Daily ingestion is handled by GitHub Actions (see .github/workflows/daily-ingestion.yml).
    logger.info("HealthFundIQ API starting up")
    from embeddings.embedder import _get_model
    _get_model()  # pre-load BGE model into memory

    yield

    logger.info("HealthFundIQ API shutting down")


app = FastAPI(
    title="HealthFundIQ API",
    description="Facts-only Global Healthcare Funds RAG Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# Base dev origins always allowed; production Vercel URL added via ALLOWED_ORIGINS env var.
_origins = [
    "http://localhost:8502", "http://127.0.0.1:8502",   # Streamlit
    "http://localhost:3000", "http://127.0.0.1:3000",   # Next.js dev
    "http://localhost:3001", "http://127.0.0.1:3001",   # Next.js alt port
]
_extra = os.getenv("ALLOWED_ORIGINS", "")
if _extra:
    _origins += [o.strip() for o in _extra.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router)
