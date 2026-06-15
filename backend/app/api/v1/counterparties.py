from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Counterparty, CounterpartyPerson
from app.schemas import (
    ConvertToHousehold,
    CounterpartyCreate,
    CounterpartyOut,
    CounterpartyUpdate,
    MergeRequest,
)
from app.services import counterparties as svc

router = APIRouter(prefix="/counterparties", tags=["counterparties"])


@router.get("", response_model=list[CounterpartyOut])
def list_counterparties(
    category: Optional[str] = None,
    kind: Optional[str] = None,
    relation: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    stmt = select(Counterparty)
    if not include_inactive:
        stmt = stmt.where(Counterparty.is_active.is_(True))
    if category:
        stmt = stmt.where(Counterparty.category == category)
    if kind:
        stmt = stmt.where(Counterparty.kind == kind)
    if relation:
        stmt = stmt.where(Counterparty.relation == relation)
    if q:
        stmt = stmt.where(Counterparty.name.like(f"%{q}%"))
    if tag:
        stmt = stmt.where(Counterparty.tags.any(name=tag))
    return db.scalars(stmt.order_by(Counterparty.id.desc())).all()


@router.post("", response_model=CounterpartyOut, status_code=201)
def create_counterparty(payload: CounterpartyCreate, db: Session = Depends(get_db)):
    cp = Counterparty(
        category=payload.category, name=payload.name, kind=payload.kind,
        relation=payload.relation, note=payload.note,
    )
    cp.persons = [CounterpartyPerson(name=p.name, role=p.role) for p in payload.persons]
    cp.tags = svc.resolve_tags(db, payload.tags)
    db.add(cp)
    db.commit()
    db.refresh(cp)
    return cp


@router.get("/{cp_id}", response_model=CounterpartyOut)
def get_counterparty(cp_id: int, db: Session = Depends(get_db)):
    return svc.get_or_404(db, cp_id)


@router.patch("/{cp_id}", response_model=CounterpartyOut)
def update_counterparty(cp_id: int, payload: CounterpartyUpdate, db: Session = Depends(get_db)):
    cp = svc.get_or_404(db, cp_id)
    data = payload.model_dump(exclude_unset=True)
    if "persons" in data:
        cp.persons = [CounterpartyPerson(name=p["name"], role=p.get("role")) for p in data.pop("persons")]
    if "tags" in data:
        cp.tags = svc.resolve_tags(db, data.pop("tags"))
    for k, v in data.items():
        setattr(cp, k, v)
    db.commit()
    db.refresh(cp)
    return cp


@router.delete("/{cp_id}", status_code=204)
def delete_counterparty(cp_id: int, db: Session = Depends(get_db)):
    cp = svc.get_or_404(db, cp_id)
    refs = svc.reference_count(db, cp_id)
    if refs:
        raise HTTPException(
            status_code=409,
            detail=f"该往来对象有 {refs} 笔往来记录，不能删除（删了会丢失人情往来历史）",
        )
    db.delete(cp)
    db.commit()


@router.post("/{cp_id}/convert-to-household", response_model=CounterpartyOut)
def convert(cp_id: int, payload: ConvertToHousehold, db: Session = Depends(get_db)):
    cp = svc.get_or_404(db, cp_id)
    svc.convert_to_household(db, cp, payload.household_name, payload.add_persons)
    db.commit()
    db.refresh(cp)
    return cp


@router.post("/{cp_id}/merge", response_model=CounterpartyOut)
def merge(cp_id: int, payload: MergeRequest, db: Session = Depends(get_db)):
    target = svc.get_or_404(db, cp_id)
    svc.merge(db, target, payload.from_id, payload.household_name)
    db.commit()
    db.refresh(target)
    return target
