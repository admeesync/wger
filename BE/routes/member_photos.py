import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from repository import member_photo_repo, user_repo
from schema.user import UserOut
from settings.settings import settings
from utils.storage import storage_service

router = APIRouter(prefix='/members/{member_id}/photo', tags=['member-photos'])


def _member_in_gym(db: Session, member_id: int, gym_id: int):
    member = user_repo.get_by_id(db, member_id)
    if member is None or member.gym_id != gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    return member


@router.get('/status')
def photo_status(member_id: int, db: Session = Depends(get_db), staff=Depends(require_gym_staff)):
    _member_in_gym(db, member_id, staff.gym_id)
    photo = member_photo_repo.get_for_member(db, member_id)
    return {'has_photo': photo is not None, 'url': storage_service.get_file_url(photo.file_path) if photo else None}


@router.post('', status_code=status.HTTP_201_CREATED)
def upload_photo(
    member_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    staff=Depends(require_gym_staff),
):
    _member_in_gym(db, member_id, staff.gym_id)
    ext = os.path.splitext(file.filename or '')[1] or '.jpg'
    filename = f'{uuid.uuid4().hex}{ext}'
    storage_service.upload_file(file.file.read(), filename)
    photo = member_photo_repo.upsert(db, member_id, filename)
    return {'url': storage_service.get_file_url(photo.file_path)}


@router.delete('', status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(member_id: int, db: Session = Depends(get_db), staff=Depends(require_gym_staff)):
    _member_in_gym(db, member_id, staff.gym_id)
    photo = member_photo_repo.get_for_member(db, member_id)
    if photo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'No photo for this member')
    storage_service.delete_file(photo.file_path)
    member_photo_repo.delete(db, photo)

