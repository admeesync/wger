from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.constants import Role
from dependencies.db import get_db
from models.user import User
from repository import user_repo
from utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_access_token(token)
    user = user_repo.get_by_id(db, int(user_id)) if user_id else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid or expired token')
    return user


def require_gym_staff(user: User = Depends(get_current_user)) -> User:
    if user.role not in Role.STAFF:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Gym staff access required')
    if user.gym_id is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'No gym assigned to this account')
    return user


def get_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Page routes use a browser cookie (not a Bearer header) so plain <form> posts and
    full-page navigations work exactly like the original Django session-based app."""
    token = request.cookies.get('access_token')
    if not token:
        return None
    user_id = decode_access_token(token)
    if not user_id:
        return None
    return user_repo.get_by_id(db, int(user_id))
