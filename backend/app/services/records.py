"""Record validation against the three-category rules and the owning event."""
from __future__ import annotations
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Counterparty, Event, Member


_CAT_OBJ = {"gift": "往来对象", "child": "孩子", "parents": "父母"}


def validate_for_event(db: Session, event: Event, counterparty_id: Optional[int],
                       member_id: Optional[int]) -> None:
    """All three categories require a counterparty whose category matches the event."""
    label = _CAT_OBJ.get(event.category, "对象")
    if counterparty_id is None:
        raise HTTPException(status_code=422, detail=f"请选择{label}")
    cp = db.get(Counterparty, counterparty_id)
    if cp is None:
        raise HTTPException(status_code=422, detail=f"{label}不存在")
    if cp.category != event.category:
        raise HTTPException(status_code=422, detail=f"所选{label}与事件类别不符")
    if member_id is not None and db.get(Member, member_id) is None:
        raise HTTPException(status_code=422, detail="记账人不存在")
