"""ORM models for 礼簿 Libu.

Entities: members (记账人), events (事件), records (流水),
counterparties (往来对象) + counterparty_persons, tags + counterparty_tags.
Money is stored as integer cents. Categories are a fixed enum: child/parents/gift.
"""
from __future__ import annotations
from typing import Optional

from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Fixed enums (hard-coded, not user-editable)
CATEGORIES = ("child", "parents", "gift")
DIRECTIONS = ("in", "out")
COUNTERPARTY_KINDS = ("person", "household")


class Member(Base):
    """记账人 — a name for the "who recorded this" dropdown. NOT a login account."""

    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Counterparty(Base):
    """往来对象 — a person (张三) or a household (张三&李四). Stable id; records reference it."""

    __tablename__ = "counterparties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(12), default="gift", nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    kind: Mapped[str] = mapped_column(String(10), default="person", nullable=False)
    relation: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    persons: Mapped[list[CounterpartyPerson]] = relationship(
        back_populates="counterparty", cascade="all, delete-orphan"
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary="counterparty_tags", back_populates="counterparties"
    )


class CounterpartyPerson(Base):
    """A named person inside a household counterparty (lets 张三&李四 split into two people)."""

    __tablename__ = "counterparty_persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("counterparties.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    counterparty: Mapped[Counterparty] = relationship(back_populates="persons")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    counterparties: Mapped[list[Counterparty]] = relationship(
        secondary="counterparty_tags", back_populates="tags"
    )


class CounterpartyTag(Base):
    __tablename__ = "counterparty_tags"

    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("counterparties.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )


class Event(Base):
    """事件 / 场合 — the container you create first, then batch-add records under it."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(12), nullable=False)
    direction: Mapped[str] = mapped_column(String(4), default="out", nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    occurred_at: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    records: Mapped[list[Record]] = relationship(back_populates="event")


class Record(Base):
    """流水 — one money line. Always belongs to an event (event_id NOT NULL)."""

    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(12), nullable=False)
    direction: Mapped[str] = mapped_column(String(4), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    subtype: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    counterparty_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("counterparties.id"), nullable=True, index=True
    )
    member_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("members.id"), nullable=True, index=True
    )
    occurred_at: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    event: Mapped[Event] = relationship(back_populates="records")
    counterparty: Mapped[Optional[Counterparty]] = relationship()
    member: Mapped[Optional[Member]] = relationship()
