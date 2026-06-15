from fastapi import APIRouter

from app.api.v1 import counterparties, events, gifts, members, records, stats, tags

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(members.router)
api_router.include_router(counterparties.router)
api_router.include_router(tags.router)
api_router.include_router(events.router)
api_router.include_router(records.router)
api_router.include_router(gifts.router)
api_router.include_router(stats.router)
