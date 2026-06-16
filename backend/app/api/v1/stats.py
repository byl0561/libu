from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Member, Record
from app.services.stats import overview as overview_svc

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
def overview(year: Optional[int] = None, month: Optional[int] = None, db: Session = Depends(get_db)):
    return overview_svc(db, year, month)


@router.get("/trend")
def trend(year: int, category: Optional[str] = None, db: Session = Depends(get_db)):
    """Per-month totals (in/out) for a single year. Returns only months with data
    (keyed "01".."12"); the client fills missing months with 0 and orders them."""
    stmt = (
        select(
            func.strftime("%m", Record.occurred_at).label("m"),
            Record.direction,
            func.coalesce(func.sum(Record.amount_cents), 0),
        )
        .where(func.strftime("%Y", Record.occurred_at) == str(year))
        .group_by("m", Record.direction)
    )
    if category:
        stmt = stmt.where(Record.category == category)
    buckets: dict[str, dict[str, int]] = {}
    for m, direction, total in db.execute(stmt).all():
        buckets.setdefault(m, {"in_cents": 0, "out_cents": 0})[f"{direction}_cents"] = int(total)
    return [{"month": m, **vals} for m, vals in sorted(buckets.items())]


@router.get("/by-member")
def by_member(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Member.name,
            func.coalesce(func.sum(Record.amount_cents), 0),
            func.count(Record.id),
        )
        .join(Record, Record.member_id == Member.id)
        .group_by(Member.id)
        .order_by(func.sum(Record.amount_cents).desc())
    ).all()
    return [{"member": r[0], "total_cents": int(r[1]), "count": int(r[2])} for r in rows]
