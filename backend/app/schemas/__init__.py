"""Pydantic v2 schemas. Money crosses the API as integer cents (amount_cents)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Category = Literal["child", "parents", "gift"]
Direction = Literal["in", "out"]
Kind = Literal["person", "household"]


# ---------- members ----------
class MemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    sort: int = 0


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    sort: Optional[int] = None


class MemberOut(MemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- tags ----------
class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)


# ---------- counterparty persons ----------
class PersonIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    role: Optional[str] = Field(default=None, max_length=20)


class PersonOut(PersonIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- counterparties ----------
class CounterpartyBase(BaseModel):
    category: Category = "gift"
    name: str = Field(min_length=1, max_length=80)
    kind: Kind = "person"
    relation: Optional[str] = Field(default=None, max_length=30)
    note: Optional[str] = Field(default=None, max_length=255)


class CounterpartyCreate(CounterpartyBase):
    persons: list[PersonIn] = []
    tags: list[str] = []


class CounterpartyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    kind: Optional[Kind] = None
    relation: Optional[str] = Field(default=None, max_length=30)
    note: Optional[str] = Field(default=None, max_length=255)
    persons: Optional[list[PersonIn]] = None
    tags: Optional[list[str]] = None


class CounterpartyOut(CounterpartyBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    persons: list[PersonOut] = []
    tags: list[TagOut] = []


class ConvertToHousehold(BaseModel):
    household_name: Optional[str] = Field(default=None, max_length=80)
    add_persons: list[PersonIn] = []


class MergeRequest(BaseModel):
    from_id: int
    household_name: Optional[str] = Field(default=None, max_length=80)


# ---------- events ----------
class EventBase(BaseModel):
    # 三类账都支持 送(out) / 收(in) 两个方向，逻辑一致。
    category: Category
    direction: Direction = "out"
    name: str = Field(min_length=1, max_length=80)
    occurred_at: date
    note: Optional[str] = Field(default=None, max_length=255)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    occurred_at: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=255)
    category: Optional[Category] = None
    direction: Optional[Direction] = None
    sync_record_dates: bool = False


class EventOut(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EventSummary(EventOut):
    record_count: int = 0
    total_cents: int = 0
    in_cents: int = 0
    out_cents: int = 0


# ---------- records ----------
class RecordIn(BaseModel):
    """A single line. When posted under /events/{id}/records, category/direction/date inherit."""

    amount_cents: int = Field(gt=0)
    subtype: Optional[str] = Field(default=None, max_length=20)
    counterparty_id: Optional[int] = None
    member_id: Optional[int] = None
    occurred_at: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=255)


class RecordCreate(RecordIn):
    event_id: int


class RecordBatchCreate(BaseModel):
    records: list[RecordIn] = Field(min_length=1)


class RecordUpdate(BaseModel):
    amount_cents: Optional[int] = Field(default=None, gt=0)
    subtype: Optional[str] = Field(default=None, max_length=20)
    counterparty_id: Optional[int] = None
    member_id: Optional[int] = None
    occurred_at: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=255)
    event_id: Optional[int] = None


class RecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_id: int
    category: Category
    direction: Direction
    amount_cents: int
    subtype: Optional[str]
    counterparty_id: Optional[int]
    member_id: Optional[int]
    occurred_at: date
    note: Optional[str]
    created_at: datetime
