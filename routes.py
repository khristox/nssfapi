# routes.py
from sqlite3 import IntegrityError
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import Session, select
import sqlite3
from models import Member, Contribution
from database import engine
from schema import MemberCreate, MemberResponse
from sqlalchemy.exc import DBAPIError, IntegrityError


router = APIRouter()

@router.post("/members", response_model=MemberResponse)
def create_member(member: MemberCreate):
    with Session(engine) as session:
        db_member = Member(**member.model_dump())
        session.add(db_member)
        try:
            session.commit()
            session.refresh(db_member)
        except DBAPIError as e:
            session.rollback()
            # Check if the underlying exception is a sqlite3.IntegrityError (or any constraint violation)
            if isinstance(e.orig, sqlite3.IntegrityError) or isinstance(e, IntegrityError):
                raise HTTPException(
                    status_code=400,
                    detail=f"Member with national_id '{member.national_id}' already exists"
                )
            # Otherwise raise a generic 500
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )
        return db_member

@router.get("/members")
def read_members(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    """
    Get members with pagination.
    - skip: number of records to skip (offset)
    - limit: number of records to return
    """
    with Session(engine) as session:
        statement = select(Member).offset(skip).limit(limit)
        members = session.exec(statement).all()
        return members

@router.get("/members/{member_id}")
def read_member(member_id: int):
    with Session(engine) as session:
        member = session.get(Member, member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        return member

@router.put("/members/{member_id}")
@router.patch("/members/{member_id}")
def update_member(member_id: int, member: Member):
    with Session(engine) as session:
        db_member = session.get(Member, member_id)
        if not db_member:
            raise HTTPException(status_code=404, detail="Member not found")
        for key, value in member.dict(exclude_unset=True).items():
            setattr(db_member, key, value)
        session.commit()
        session.refresh(db_member)
        return db_member

@router.delete("/members/{member_id}")
def delete_member(member_id: int):
    with Session(engine) as session:
        member = session.get(Member, member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        session.delete(member)
        session.commit()
        return {"ok": True}

@router.post("/contributions/")
def add_contribution(contribution: Contribution):
    with Session(engine) as session:
        member = session.get(Member, contribution.member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        session.add(contribution)
        try:
            session.commit()
            session.refresh(contribution)
        except DBAPIError as e:
            session.rollback()
            # Check if underlying DBAPI error is sqlite3.IntegrityError
            if isinstance(e.orig, sqlite3.IntegrityError) or isinstance(e, IntegrityError):
                raise HTTPException(
                    status_code=400,
                    detail=f"Duplicate contribution for member_id '{contribution.member_id}' for month '{contribution.month}' with amount '{contribution.amount}'"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error: {str(e)}"
                )
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )
        return contribution

@router.get("/members/{member_id}/contributions")
def get_member_contributions(member_id: int):
    with Session(engine) as session:
        statement = (
            select(Contribution, Member)
            .join(Member, Member.id == Contribution.member_id)
            .where(Member.id == member_id)
        )
        results = session.exec(statement).all()

        if not results:
            raise HTTPException(status_code=404, detail="No contributions found for this member")

        contributions = [
            {
                "id": contribution.id,
                "member_name": member.name,
                "member_id":member.national_id,
                "amount": contribution.amount,
                "month": contribution.month,
            }
            for contribution, member in results
        ]
        return contributions
