from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Event, Record
from app.schemas import (
    EventCreate,
    EventOut,
    EventSummary,
    EventUpdate,
    RecordBatchCreate,
    RecordOut,
)
from app.services.records import validate_for_event

router = APIRouter(prefix="/events", tags=["events"])


def _summary_row(db: Session, event: Event) -> EventSummary:
    in_sum, out_sum, cnt = db.execute(
        select(
            func.coalesce(func.sum(case((Record.direction == "in", Record.amount_cents), else_=0)), 0),
            func.coalesce(func.sum(case((Record.direction == "out", Record.amount_cents), else_=0)), 0),
            func.count(Record.id),
        ).where(Record.event_id == event.id, Record.deleted_at.is_(None))
    ).one()
    data = EventSummary.model_validate(event)
    data.in_cents = int(in_sum)
    data.out_cents = int(out_sum)
    data.total_cents = int(in_sum) + int(out_sum)
    data.record_count = int(cnt)
    return data


@router.get("", response_model=list[EventSummary])
def list_events(
    category: Optional[str] = None,
    direction: Optional[str] = None,
    from_: Optional[date] = None,
    to: Optional[date] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    stmt = select(Event)
    if category:
        stmt = stmt.where(Event.category == category)
    if direction:
        stmt = stmt.where(Event.direction == direction)
    if from_:
        stmt = stmt.where(Event.occurred_at >= from_)
    if to:
        stmt = stmt.where(Event.occurred_at <= to)
    if q:
        stmt = stmt.where(Event.name.like(f"%{q}%"))
    events = db.scalars(stmt.order_by(Event.occurred_at.desc(), Event.id.desc())).all()
    return [_summary_row(db, e) for e in events]


@router.post("", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="事件不存在")
    records = db.scalars(
        select(Record)
        .where(Record.event_id == event_id, Record.deleted_at.is_(None))
        .order_by(Record.occurred_at.desc(), Record.id.desc())
    ).all()
    return {
        "event": _summary_row(db, event),
        "records": [RecordOut.model_validate(r) for r in records],
    }


@router.patch("/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="事件不存在")
    data = payload.model_dump(exclude_unset=True)
    sync_dates = data.pop("sync_record_dates", False)
    has_records = db.scalar(
        select(func.count()).select_from(Record).where(
            Record.event_id == event_id, Record.deleted_at.is_(None)
        )
    )

    # category/direction are locked once records exist (they inherit from the event).
    if has_records and ("category" in data or "direction" in data):
        raise HTTPException(status_code=409, detail="事件下已有流水，不能改类型/方向")

    old_date = event.occurred_at
    for k, v in data.items():
        setattr(event, k, v)

    if sync_dates and "occurred_at" in data and event.occurred_at != old_date:
        db.query(Record).filter(
            Record.event_id == event_id, Record.occurred_at == old_date
        ).update({Record.occurred_at: event.occurred_at}, synchronize_session=False)

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="事件不存在")
    refs = db.scalar(
        select(func.count()).select_from(Record).where(
            Record.event_id == event_id, Record.deleted_at.is_(None)
        )
    )
    if refs:
        raise HTTPException(
            status_code=409,
            detail=f"事件下有 {refs} 笔流水，不能删除；不想要可归档(is_closed=true)",
        )
    db.delete(event)
    db.commit()


@router.post("/{event_id}/records", response_model=list[RecordOut], status_code=201)
def batch_add_records(event_id: int, payload: RecordBatchCreate, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="事件不存在")
    if event.is_closed:
        raise HTTPException(status_code=409, detail="事件已归档，不能再加流水")

    created: list[Record] = []
    for item in payload.records:
        validate_for_event(db, event, item.counterparty_id, item.member_id)
        rec = Record(
            event_id=event.id,
            category=event.category,
            direction=event.direction,
            amount_cents=item.amount_cents,
            subtype=item.subtype,
            counterparty_id=item.counterparty_id,
            member_id=item.member_id,
            occurred_at=item.occurred_at or event.occurred_at,
            note=item.note,
        )
        db.add(rec)
        created.append(rec)
    db.commit()
    for rec in created:
        db.refresh(rec)
    return created
