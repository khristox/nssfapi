from sqlmodel import Column, SQLModel, Field, Relationship,Date, UniqueConstraint
from typing import Optional, List
from datetime import date


class Contribution(SQLModel, table=True):
    __table_args__ = (
        # Composite unique constraint on member_id + month
        UniqueConstraint("member_id", "month", name="uq_member_month"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="member.id")
    amount: float
    month: str
    member: Optional["Member"] = Relationship(back_populates="contributions")

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    national_id: str= Field(sa_column_kwargs={"unique": True})
    date_joined: date = Field(nullable=False)
    contributions: List[Contribution] = Relationship(
        back_populates="member",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
