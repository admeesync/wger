import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.member import Member
from models.member_document import MemberDocument
from models.user import User
from repository import member_document_repo, member_repo
from schema.member_document import MemberDocumentOut
from settings.settings import settings

router = APIRouter(prefix='/members/{member_id}/documents', tags=['member-documents'])


def _member_in_gym(db: Session, member_id: int, gym_id: int) -> Member:
    member = member_repo.get_by_id(db, member_id)
    if member is None or member.gym_id != gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    return member


@router.get('', response_model=list[MemberDocumentOut])
def list_documents(member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    _member_in_gym(db, member_id, staff.gym_id)
    return member_document_repo.list_for_member(db, member_id)


@router.post('', response_model=MemberDocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    member_id: int, file: UploadFile, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
):
    _member_in_gym(db, member_id, staff.gym_id)
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or '')[1] or '.pdf'
    filename = f'{uuid.uuid4().hex}{ext}'
    with open(os.path.join(settings.upload_dir, filename), 'wb') as f:
        f.write(file.file.read())
    document = MemberDocument(
        member_id=member_id, file_path=filename,
        original_name=file.filename or filename, uploaded_at=datetime.utcnow(),
    )
    return member_document_repo.create(db, document)


@router.delete('/{document_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    member_id: int, document_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
):
    _member_in_gym(db, member_id, staff.gym_id)
    document = member_document_repo.get_by_id(db, document_id)
    if document is None or document.member_id != member_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Document not found')
    path = os.path.join(settings.upload_dir, document.file_path)
    if os.path.exists(path):
        os.remove(path)
    member_document_repo.delete(db, document)
