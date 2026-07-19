import io
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from PIL import Image, ImageSequence, UnidentifiedImageError
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.photo_upload_token import PhotoUploadToken
from repository import member_photo_repo, member_repo, photo_upload_token_repo
from utils import supabase_storage

router = APIRouter(prefix='/members/{member_id}/photo', tags=['member-photos'])
public_router = APIRouter(prefix='/public/photo-upload', tags=['member-photos'])

TOKEN_VALID_MINUTES = 15
MAX_DIMENSION = 800


def _member_in_gym(db: Session, member_id: int, gym_id: int):
    member = member_repo.get_by_id(db, member_id)
    if member is None or member.gym_id != gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    return member


def _compress_image(file: UploadFile) -> tuple[bytes, str, str]:
    try:
        img = Image.open(file.file)
        img.load()
    except UnidentifiedImageError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Only image files are allowed')

    buf = io.BytesIO()
    if getattr(img, 'is_animated', False):
        frames = []
        for frame in ImageSequence.Iterator(img):
            f = frame.convert('RGBA')
            f.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
            frames.append(f)
        frames[0].save(
            buf, format='GIF', save_all=True, append_images=frames[1:],
            optimize=True, loop=img.info.get('loop', 0), duration=img.info.get('duration', 100),
        )
        return buf.getvalue(), '.gif', 'image/gif'

    img = img.convert('RGB')
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
    img.save(buf, format='JPEG', quality=70, optimize=True)
    return buf.getvalue(), '.jpg', 'image/jpeg'


def _save_upload(file: UploadFile) -> str:
    data, ext, content_type = _compress_image(file)
    filename = f'{uuid.uuid4().hex}{ext}'
    supabase_storage.upload(filename, data, content_type)
    return filename


@router.get('/status')
def photo_status(member_id: int, db: Session = Depends(get_db), staff=Depends(require_gym_staff)):
    _member_in_gym(db, member_id, staff.gym_id)
    photo = member_photo_repo.get_for_member(db, member_id)
    return {'has_photo': photo is not None, 'url': supabase_storage.signed_url(photo.file_path) if photo else None}


@router.post('', status_code=status.HTTP_201_CREATED)
def upload_photo(
    member_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    staff=Depends(require_gym_staff),
):
    _member_in_gym(db, member_id, staff.gym_id)
    filename = _save_upload(file)
    photo = member_photo_repo.upsert(db, member_id, filename)
    return {'url': supabase_storage.signed_url(photo.file_path)}


@router.delete('', status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(member_id: int, db: Session = Depends(get_db), staff=Depends(require_gym_staff)):
    _member_in_gym(db, member_id, staff.gym_id)
    photo = member_photo_repo.get_for_member(db, member_id)
    if photo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'No photo for this member')
    supabase_storage.delete(photo.file_path)
    member_photo_repo.delete(db, photo)


@router.post('/qr-token')
def generate_upload_token(member_id: int, db: Session = Depends(get_db), staff=Depends(require_gym_staff)):
    """Mints a short-lived, single-use token so the member can scan a QR code
    and upload their own photo from their phone camera, without logging in."""
    member = _member_in_gym(db, member_id, staff.gym_id)
    photo_upload_token_repo.invalidate_for_member(db, member_id)
    token_obj = photo_upload_token_repo.create(db, PhotoUploadToken(
        member_id=member.id, token=uuid.uuid4().hex,
        expires_at=datetime.utcnow() + timedelta(minutes=TOKEN_VALID_MINUTES),
    ))
    return {'token': token_obj.token, 'expires_at': token_obj.expires_at}


def _get_valid_token(db: Session, token: str) -> PhotoUploadToken:
    token_obj = photo_upload_token_repo.get_by_token(db, token)
    if token_obj is None or token_obj.used or token_obj.expires_at < datetime.utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'This upload link has expired. Ask the gym to generate a new QR code.')
    return token_obj


@public_router.get('/{token}')
def check_upload_token(token: str, db: Session = Depends(get_db)):
    token_obj = _get_valid_token(db, token)
    member = member_repo.get_by_id(db, token_obj.member_id)
    return {'valid': True, 'member_name': member.get_full_name() if member else 'Member'}


@public_router.post('/{token}')
def public_upload_photo(token: str, file: UploadFile, db: Session = Depends(get_db)):
    token_obj = _get_valid_token(db, token)
    filename = _save_upload(file)
    member_photo_repo.upsert(db, token_obj.member_id, filename)
    token_obj.used = True
    photo_upload_token_repo.save(db, token_obj)
    return {'ok': True}
