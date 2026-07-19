from sqlalchemy.orm import Session

from models.member import Member


def get_by_id(db: Session, member_id: int) -> Member | None:
    return db.query(Member).filter(Member.id == member_id).first()


def get_by_username(db: Session, username: str) -> Member | None:
    return db.query(Member).filter(Member.username == username).first()


def get_by_email(db: Session, email: str) -> Member | None:
    return db.query(Member).filter(Member.email == email).first()


def get_by_device_user_id(db: Session, gym_id: int, device_user_id: str) -> Member | None:
    return (
        db.query(Member)
        .filter(Member.gym_id == gym_id, Member.device_user_id == device_user_id)
        .first()
    )


def list_by_gym(db: Session, gym_id: int) -> list[Member]:
    return db.query(Member).filter(Member.gym_id == gym_id).order_by(Member.username).all()


def get_owner_in_gym(db: Session, gym_id: int) -> Member | None:
    return db.query(Member).filter(Member.gym_id == gym_id, Member.member_type == 'owner').first()


def recent_by_gym(db: Session, gym_id: int, limit: int = 5) -> list[Member]:
    return (
        db.query(Member)
        .filter(Member.gym_id == gym_id)
        .order_by(Member.date_joined.desc())
        .limit(limit)
        .all()
    )


def create(db: Session, member: Member) -> Member:
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def delete(db: Session, member: Member) -> None:
    db.delete(member)
    db.commit()
