"""First-boot seed: create tables and ensure the 记账人 dropdown is non-empty."""
from sqlalchemy import select

from app.core.config import settings
from app.db.base import Base, SessionLocal, engine
from app.models import Member

# Subtype options live in code (not a DB table); the frontend reads these for dropdowns.
SUBTYPES = {
    "child": ["supplies", "education", "medical", "other"],
    "parents": ["cash", "medical", "health", "other"],
    "gift": [],
}


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing = db.scalar(select(Member).limit(1))
        if existing is None:
            names = [n.strip() for n in settings.default_members.split(",") if n.strip()]
            for i, name in enumerate(names or ["我"]):
                db.add(Member(name=name, sort=i))
            db.commit()
