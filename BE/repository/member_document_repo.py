from sqlalchemy.orm import Session

from models.member_document import MemberDocument


def list_for_member(db: Session, member_id: int) -> list[MemberDocument]:
    return (
        db.query(MemberDocument)
        .filter(MemberDocument.member_id == member_id)
        .order_by(MemberDocument.uploaded_at.desc())
        .all()
    )


def get_by_id(db: Session, document_id: int) -> MemberDocument | None:
    return db.query(MemberDocument).filter(MemberDocument.id == document_id).first()


def create(db: Session, document: MemberDocument) -> MemberDocument:
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def delete(db: Session, document: MemberDocument) -> None:
    db.delete(document)
    db.commit()
