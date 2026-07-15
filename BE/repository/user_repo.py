from sqlalchemy.orm import Session

from models.user import User


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def list_by_gym(db: Session, gym_id: int) -> list[User]:
    return (
        db.query(User)
        .filter(User.gym_id == gym_id, User.role == 'member')
        .order_by(User.username)
        .all()
    )


def recent_by_gym(db: Session, gym_id: int, limit: int = 5) -> list[User]:
    return (
        db.query(User)
        .filter(User.gym_id == gym_id, User.role == 'member')
        .order_by(User.date_joined.desc())
        .limit(limit)
        .all()
    )


def create(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
