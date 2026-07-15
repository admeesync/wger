from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.inquiry import Inquiry
from models.user import User
from repository import inquiry_repo
from schema.inquiry import InquiryCreate, InquiryOut, InquiryStatusUpdate

router = APIRouter(prefix='/inquiries', tags=['inquiries'])


def _get_inquiry_in_gym(db: Session, inquiry_id: int, gym_id: int) -> Inquiry:
    inquiry = inquiry_repo.get_in_gym(db, inquiry_id, gym_id)
    if inquiry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Inquiry not found')
    return inquiry


@router.get('', response_model=list[InquiryOut])
def list_inquiries(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return inquiry_repo.list_for_gym(db, staff.gym_id)


@router.post('', response_model=InquiryOut, status_code=status.HTTP_201_CREATED)
def add_inquiry(data: InquiryCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    inquiry = Inquiry(gym_id=staff.gym_id, date_created=date.today(), **data.model_dump())
    return inquiry_repo.create(db, inquiry)


@router.post('/{inquiry_id}/status', response_model=InquiryOut)
def set_status(
    inquiry_id: int,
    data: InquiryStatusUpdate,
    db: Session = Depends(get_db),
    staff: User = Depends(require_gym_staff),
):
    inquiry = _get_inquiry_in_gym(db, inquiry_id, staff.gym_id)
    inquiry.status = data.status
    return inquiry_repo.save(db, inquiry)


@router.delete('/{inquiry_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_inquiry(inquiry_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    inquiry = _get_inquiry_in_gym(db, inquiry_id, staff.gym_id)
    inquiry_repo.delete(db, inquiry)
