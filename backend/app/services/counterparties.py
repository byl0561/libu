"""Counterparty helpers: tag resolution, household conversion, and merge."""
from __future__ import annotations
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Counterparty, CounterpartyPerson, CounterpartyTag, Record, Tag


def resolve_tags(db: Session, names: list[str]) -> list[Tag]:
    """Get-or-create tags by name."""
    tags: list[Tag] = []
    for raw in names:
        name = raw.strip()
        if not name:
            continue
        tag = db.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def reference_count(db: Session, counterparty_id: int) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Record)
        .where(Record.counterparty_id == counterparty_id)
    ) or 0


def get_or_404(db: Session, counterparty_id: int) -> Counterparty:
    cp = db.get(Counterparty, counterparty_id)
    if cp is None:
        raise HTTPException(status_code=404, detail="往来对象不存在")
    return cp


def convert_to_household(
    db: Session, cp: Counterparty, household_name: Optional[str], add_persons: list
) -> Counterparty:
    """Promote a person to a household and add members. History follows automatically."""
    cp.kind = "household"
    if household_name:
        cp.name = household_name
    existing_names = {p.name for p in cp.persons}
    # Keep the original individual as a person of the household if not already listed.
    if not cp.persons:
        cp.persons.append(CounterpartyPerson(name=cp.name.split("&")[0]))
        existing_names.add(cp.name.split("&")[0])
    for p in add_persons:
        if p.name not in existing_names:
            cp.persons.append(CounterpartyPerson(name=p.name, role=p.role))
    db.flush()
    return cp


def merge(db: Session, target: Counterparty, from_id: int, household_name: Optional[str]) -> Counterparty:
    """Merge `from_id` into `target`: repoint records, fold in persons/tags, delete source."""
    if from_id == target.id:
        raise HTTPException(status_code=400, detail="不能与自身合并")
    source = db.get(Counterparty, from_id)
    if source is None:
        raise HTTPException(status_code=404, detail="被合并对象不存在")
    if source.category != target.category:
        raise HTTPException(status_code=400, detail="只能合并同类别的对象")

    # 1. repoint all of source's records to target
    db.query(Record).filter(Record.counterparty_id == from_id).update(
        {Record.counterparty_id: target.id}, synchronize_session=False
    )

    # 2. fold persons in. Seed the target's own name first (so 张三 isn't lost when it
    #    had no person rows of its own), then add the source's people.
    target_names = {p.name for p in target.persons}
    source_names = {source.name, *(p.name for p in source.persons)}
    seed_names = ([target.name] if not target.persons else []) + sorted(source_names)
    for name in seed_names:
        base = name.split("&")[0]
        if base and base not in target_names:
            target.persons.append(CounterpartyPerson(name=base))
            target_names.add(base)

    # 3. merge tags (dedupe)
    target_tag_ids = {t.id for t in target.tags}
    for t in source.tags:
        if t.id not in target_tag_ids:
            target.tags.append(t)
    db.query(CounterpartyTag).filter(CounterpartyTag.counterparty_id == from_id).delete(
        synchronize_session=False
    )

    # 4. upgrade target and delete the source (its records/tags are repointed away,
    #    its persons cascade-delete) — 所见即所得, no hidden leftovers.
    target.kind = "household"
    target.name = household_name or target.name
    db.delete(source)
    db.flush()
    return target
