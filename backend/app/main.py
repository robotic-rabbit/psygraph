from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.quiz import router as quiz_router
from app.config import get_settings
from app.db.session import AsyncSessionLocal, init_db
from app.dependencies import get_scoring_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scoring_svc = get_scoring_service()
    async with AsyncSessionLocal() as db:
        await scoring_svc.load_matrix(db)
    yield


settings = get_settings()

app = FastAPI(title="Unified SWCPQ API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz_router)
