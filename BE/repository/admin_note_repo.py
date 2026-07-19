from sqlalchemy.orm import Session

from models.admin_note import AdminNote


def list_for_member(db: Session, member_id: int) -> list[AdminNote]:
    return db.query(AdminNote).filter(AdminNote.member_id == member_id).order_by(AdminNote.created_at.desc()).all()


def get_by_id(db: Session, note_id: int) -> AdminNote | None:
    return db.query(AdminNote).filter(AdminNote.id == note_id).first()


def create(db: Session, note: AdminNote) -> AdminNote:
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def delete(db: Session, note: AdminNote) -> None:
    db.delete(note)
    db.commit()
