from sqlalchemy.orm import Session

from models.inquiry import Inquiry


def list_for_gym(db: Session, gym_id: int) -> list[Inquiry]:
    return db.query(Inquiry).filter(Inquiry.gym_id == gym_id).order_by(Inquiry.date_created.desc()).all()


def get_in_gym(db: Session, inquiry_id: int, gym_id: int) -> Inquiry | None:
    return db.query(Inquiry).filter(Inquiry.id == inquiry_id, Inquiry.gym_id == gym_id).first()


def create(db: Session, inquiry: Inquiry) -> Inquiry:
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


def save(db: Session, inquiry: Inquiry) -> Inquiry:
    db.commit()
    db.refresh(inquiry)
    return inquiry


def delete(db: Session, inquiry: Inquiry) -> None:
    db.delete(inquiry)
    db.commit()
