"""Aggregation for the gift ledger and overview stats."""
from __future__ import annotations
from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Counterparty, Record


def _net_expr():
    return func.sum(
        case((Record.direction == "in", Record.amount_cents), else_=-Record.amount_cents)
    )


def gift_ledger(db: Session, category: Optional[str] = None,
                relation: Optional[str] = None, q: Optional[str] = None):
    """Per-counterparty rollup (any category): out / in / net / count / last date."""
    in_sum = func.coalesce(
        func.sum(case((Record.direction == "in", Record.amount_cents), else_=0)), 0
    )
    out_sum = func.coalesce(
        func.sum(case((Record.direction == "out", Record.amount_cents), else_=0)), 0
    )
    stmt = (
        select(
            Counterparty.id,
            Counterparty.category,
            Counterparty.name,
            Counterparty.kind,
            Counterparty.relation,
            out_sum.label("out_cents"),
            in_sum.label("in_cents"),
            func.count(Record.id).label("count"),
            func.max(Record.occurred_at).label("last_at"),
        )
        .join(Record, Record.counterparty_id == Counterparty.id)
        .group_by(Counterparty.id)
        .order_by(func.max(Record.occurred_at).desc())
    )
    if category:
        stmt = stmt.where(Counterparty.category == category)
    if relation:
        stmt = stmt.where(Counterparty.relation == relation)
    if q:
        stmt = stmt.where(Counterparty.name.like(f"%{q}%"))

    rows = db.execute(stmt).all()
    return [
        {
            "counterparty_id": r.id,
            "category": r.category,
            "name": r.name,
            "kind": r.kind,
            "relation": r.relation,
            "out_cents": int(r.out_cents),
            "in_cents": int(r.in_cents),
            "net_cents": int(r.in_cents) - int(r.out_cents),
            "count": int(r.count),
            "last_at": r.last_at,
        }
        for r in rows
    ]


def overview(db: Session, year: Optional[int], month: Optional[int]):
    """Totals per category for a year (and optional month)."""
    stmt = select(
        Record.category,
        Record.direction,
        func.coalesce(func.sum(Record.amount_cents), 0),
    )
    if year:
        stmt = stmt.where(func.strftime("%Y", Record.occurred_at) == str(year))
    if month:
        stmt = stmt.where(func.strftime("%m", Record.occurred_at) == f"{month:02d}")
    stmt = stmt.group_by(Record.category, Record.direction)

    # All three categories now track 送(out) / 收(in) / 净(net) uniformly.
    out = {c: {"in_cents": 0, "out_cents": 0, "net_cents": 0} for c in ("child", "parents", "gift")}
    for category, direction, total in db.execute(stmt).all():
        out[category][f"{direction}_cents"] += int(total)
    for c in out.values():
        c["net_cents"] = c["in_cents"] - c["out_cents"]
    return out
