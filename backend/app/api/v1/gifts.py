from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Counterparty, Event, Record
from app.schemas import RecordOut
from app.services.stats import gift_ledger

router = APIRouter(prefix="/gifts", tags=["gifts"])


@router.get("/ledger")
def ledger(category: Optional[str] = None, relation: Optional[str] = None,
           q: Optional[str] = None, db: Session = Depends(get_db)):
    """Per-counterparty rollup (any category): out / in / net / count / last —还礼视角."""
    return gift_ledger(db, category=category, relation=relation, q=q)


@router.get("/ledger/{counterparty_id}")
def ledger_detail(counterparty_id: int, db: Session = Depends(get_db)):
    cp = db.get(Counterparty, counterparty_id)
    if cp is None:
        raise HTTPException(status_code=404, detail="往来对象不存在")
    rows = db.execute(
        select(Record, Event.name)
        .join(Event, Record.event_id == Event.id)
        .where(Record.counterparty_id == counterparty_id)
        .order_by(Record.occurred_at.desc(), Record.id.desc())
    ).all()
    return {
        "counterparty_id": cp.id,
        "name": cp.name,
        "records": [
            {
                "id": r.id,
                "event_id": r.event_id,
                "event_name": event_name,
                "direction": r.direction,
                "amount_cents": r.amount_cents,
                "occurred_at": r.occurred_at,
                "note": r.note,
            }
            for r, event_name in rows
        ],
    }


@router.get("/by-relation")
def by_relation(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Counterparty.relation,
            func.coalesce(func.sum(Record.amount_cents), 0),
            func.count(Record.id),
        )
        .join(Record, Record.counterparty_id == Counterparty.id)
        .where(Record.category == "gift")
        .group_by(Counterparty.relation)
    ).all()
    return [
        {"relation": r[0] or "未分类", "total_cents": int(r[1]), "count": int(r[2])} for r in rows
    ]


@router.get("/by-event")
def by_event(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Event.id,
            Event.name,
            Event.direction,
            func.coalesce(func.sum(Record.amount_cents), 0),
            func.count(Record.id),
        )
        .join(Record, Record.event_id == Event.id)
        .where(Record.category == "gift")
        .group_by(Event.id)
        .order_by(func.sum(Record.amount_cents).desc())
    ).all()
    return [
        {
            "event_id": r[0],
            "name": r[1],
            "direction": r[2],
            "total_cents": int(r[3]),
            "count": int(r[4]),
        }
        for r in rows
    ]
