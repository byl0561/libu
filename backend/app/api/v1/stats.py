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
def trend(category: Optional[str] = None, months: int = 12, db: Session = Depends(get_db)):
    """Monthly totals (out, and in for gift) for the last N months."""
    stmt = (
        select(
            func.strftime("%Y-%m", Record.occurred_at).label("ym"),
            Record.direction,
            func.coalesce(func.sum(Record.amount_cents), 0),
        )
        .where(Record.deleted_at.is_(None))
        .group_by("ym", Record.direction)
        .order_by("ym")
    )
    if category:
        stmt = stmt.where(Record.category == category)
    buckets: dict[str, dict[str, int]] = {}
    for ym, direction, total in db.execute(stmt).all():
        buckets.setdefault(ym, {"in_cents": 0, "out_cents": 0})[f"{direction}_cents"] = int(total)
    series = [{"month": ym, **vals} for ym, vals in sorted(buckets.items())]
    return series[-months:]


@router.get("/by-member")
def by_member(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Member.name,
            func.coalesce(func.sum(Record.amount_cents), 0),
            func.count(Record.id),
        )
        .join(Record, Record.member_id == Member.id)
        .where(Record.deleted_at.is_(None))
        .group_by(Member.id)
        .order_by(func.sum(Record.amount_cents).desc())
    ).all()
    return [{"member": r[0], "total_cents": int(r[1]), "count": int(r[2])} for r in rows]
