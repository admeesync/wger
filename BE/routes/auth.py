from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import get_current_user
from dependencies.db import get_db
from models.user import User
from schema.auth import LoginIn, RegisterIn, Token
from schema.user import UserOut
from service import auth_service

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    try:
        return auth_service.register(db, data)
    except auth_service.AuthError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post('/login', response_model=Token)
def login(data: LoginIn, db: Session = Depends(get_db)):
    try:
        token = auth_service.login(db, data.username, data.password)
    except auth_service.AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    return Token(access_token=token)


@router.get('/me', response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
