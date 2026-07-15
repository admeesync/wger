from datetime import datetime

from sqlalchemy.orm import Session

from models.gym import Gym
from models.user import User
from repository import gym_repo, license_key_repo, user_repo
from schema.auth import RegisterIn
from utils.security import create_access_token, hash_password, verify_password


class AuthError(Exception):
    pass


def register(db: Session, data: RegisterIn) -> User:
    if user_repo.get_by_username(db, data.username) or user_repo.get_by_email(db, data.email):
        raise AuthError('Username or email already registered')

    license_key = license_key_repo.get_by_key(db, data.license_key)
    if license_key is None:
        raise AuthError('Invalid license key')

    gym = gym_repo.create(db, Gym(name=data.gym_name))

    user = user_repo.create(
        db,
        User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            role='gym_admin',
            gym_id=gym.id,
            first_name=data.first_name,
            last_name=data.last_name,
        ),
    )

    license_key.is_used = True
    license_key.used_by_id = user.id
    license_key.used_at = datetime.utcnow()
    db.commit()

    return user


def login(db: Session, username: str, password: str) -> str:
    user = user_repo.get_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        raise AuthError('Invalid credentials')
    return create_access_token(subject=str(user.id))
