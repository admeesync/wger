from sqlalchemy.orm import Session

from models.user import User


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_by_device_user_id(db: Session, gym_id: int, device_user_id: str) -> User | None:
    return (
        db.query(User)
        .filter(User.gym_id == gym_id, User.device_user_id == device_user_id)
        .first()
    )


def create(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
