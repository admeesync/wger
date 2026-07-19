from sqlalchemy.orm import Session

from models.photo_upload_token import PhotoUploadToken


def get_by_token(db: Session, token: str) -> PhotoUploadToken | None:
    return db.query(PhotoUploadToken).filter(PhotoUploadToken.token == token).first()


def invalidate_for_member(db: Session, member_id: int) -> None:
    db.query(PhotoUploadToken).filter(
        PhotoUploadToken.member_id == member_id, PhotoUploadToken.used.is_(False),
    ).delete()
    db.commit()


def create(db: Session, token_obj: PhotoUploadToken) -> PhotoUploadToken:
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return token_obj


def save(db: Session, token_obj: PhotoUploadToken) -> PhotoUploadToken:
    db.commit()
    db.refresh(token_obj)
    return token_obj
