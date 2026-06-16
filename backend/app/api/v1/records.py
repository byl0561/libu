from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Event, Record
from app.schemas import RecordCreate, RecordOut, RecordUpdate
from app.services.records import validate_for_event

router = APIRouter(prefix="/records", tags=["records"])


@router.get("", response_model=list[RecordOut])
def list_records(
    event_id: Optional[int] = None,
    category: Optional[str] = None,
    direction: Optional[str] = None,
    counterparty_id: Optional[int] = None,
    member_id: Optional[int] = None,
    from_: Optional[date] = None,
    to: Optional[date] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    stmt = select(Record)
    if event_id:
        stmt = stmt.where(Record.event_id == event_id)
    if category:
        stmt = stmt.where(Record.category == category)
    if direction:
        stmt = stmt.where(Record.direction == direction)
    if counterparty_id:
        stmt = stmt.where(Record.counterparty_id == counterparty_id)
    if member_id:
        stmt = stmt.where(Record.member_id == member_id)
    if from_:
        stmt = stmt.where(Record.occurred_at >= from_)
    if to:
        stmt = stmt.where(Record.occurred_at <= to)
    if q:
        stmt = stmt.where(Record.note.like(f"%{q}%"))
    return db.scalars(stmt.order_by(Record.occurred_at.desc(), Record.id.desc())).all()


@router.post("", response_model=RecordOut, status_code=201)
def create_record(payload: RecordCreate, db: Session = Depends(get_db)):
    event = db.get(Event, payload.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="事件不存在")
    validate_for_event(db, event, payload.counterparty_id, payload.member_id)
    rec = Record(
        event_id=event.id,
        category=event.category,
        direction=event.direction,
        amount_cents=payload.amount_cents,
        subtype=payload.subtype,
        counterparty_id=payload.counterparty_id,
        member_id=payload.member_id,
        occurred_at=payload.occurred_at or event.occurred_at,
        note=payload.note,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/{record_id}", response_model=RecordOut)
def get_record(record_id: int, db: Session = Depends(get_db)):
    rec = db.get(Record, record_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return rec


@router.patch("/{record_id}", response_model=RecordOut)
def update_record(record_id: int, payload: RecordUpdate, db: Session = Depends(get_db)):
    rec = db.get(Record, record_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    data = payload.model_dump(exclude_unset=True)

    # Moving to another event re-inherits category/direction and re-validates.
    if "event_id" in data and data["event_id"] != rec.event_id:
        event = db.get(Event, data["event_id"])
        if event is None:
            raise HTTPException(status_code=404, detail="目标事件不存在")
        rec.event_id = event.id
        rec.category = event.category
        rec.direction = event.direction

    target_event = db.get(Event, rec.event_id)
    cp_id = data.get("counterparty_id", rec.counterparty_id)
    member_id = data.get("member_id", rec.member_id)
    validate_for_event(db, target_event, cp_id, member_id)

    for k, v in data.items():
        if k == "event_id":
            continue
        setattr(rec, k, v)
    db.commit()
    db.refresh(rec)
    return rec


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    rec = db.get(Record, record_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(rec)
    db.commit()
