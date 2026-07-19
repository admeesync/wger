from sqlalchemy.orm import Session

from models.member_photo import MemberPhoto


def get_for_member(db: Session, member_id: int) -> MemberPhoto | None:
    return db.query(MemberPhoto).filter(MemberPhoto.member_id == member_id).first()


def upsert(db: Session, member_id: int, file_path: str) -> MemberPhoto:
    photo = get_for_member(db, member_id)
    if photo is None:
        photo = MemberPhoto(member_id=member_id, file_path=file_path)
        db.add(photo)
    else:
        photo.file_path = file_path
    db.commit()
    db.refresh(photo)
    return photo


def delete(db: Session, photo: MemberPhoto) -> None:
    db.delete(photo)
    db.commit()
