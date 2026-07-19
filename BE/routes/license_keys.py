from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import get_current_user
from dependencies.db import get_db
from models.user import User
from repository import license_key_repo
from schema.license_key import LicenseKeyOut

router = APIRouter(prefix='/license-keys', tags=['license-keys'])


@router.post('', response_model=list[LicenseKeyOut], status_code=status.HTTP_201_CREATED)
def generate_keys(count: int = 1, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != 'super_admin':
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Only super admins can generate license keys')
    return license_key_repo.create_many(db, count)
