"""Dependency injection — DB session only (no auth; access control is nginx Basic Auth)."""
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
