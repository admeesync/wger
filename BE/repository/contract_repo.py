from datetime import date

from sqlalchemy.orm import Session

from models.contract import Contract
from models.user import User


def list_for_gym(db: Session, gym_id: int) -> list[Contract]:
    return db.query(Contract).join(User, Contract.member_id == User.id).filter(User.gym_id == gym_id).all()


def list_for_member(db: Session, member_id: int) -> list[Contract]:
    return (
        db.query(Contract)
        .filter(Contract.member_id == member_id)
        .order_by(Contract.date_start.desc())
        .all()
    )


def latest_for_member(db: Session, member_id: int) -> Contract | None:
    return (
        db.query(Contract)
        .filter(Contract.member_id == member_id)
        .order_by(Contract.date_start.desc())
        .first()
    )


def latest_for_members(db: Session, member_ids: list[int]) -> dict[int, Contract]:
    if not member_ids:
        return {}
    rows = (
        db.query(Contract)
        .filter(Contract.member_id.in_(member_ids))
        .order_by(Contract.member_id, Contract.date_start.desc())
        .all()
    )
    latest: dict[int, Contract] = {}
    for row in rows:
        latest.setdefault(row.member_id, row)
    return latest


def create(db: Session, contract: Contract) -> Contract:
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract
