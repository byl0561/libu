"""礼簿 Libu — FastAPI entrypoint. No auth here; access control is nginx Basic Auth upstream."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.db.seed import SUBTYPES, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="礼簿 Libu API", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/meta")
def meta():
    """Static enums the frontend needs (categories, subtype options)."""
    return {
        "categories": ["child", "parents", "gift"],
        "category_labels": {"child": "子女", "parents": "父母", "gift": "人情往来"},
        "directions": {"in": "收礼", "out": "送礼"},
        "subtypes": SUBTYPES,
    }
