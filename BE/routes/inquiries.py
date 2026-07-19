from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.constants import InquiryTag
from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.inquiry import Inquiry
from models.user import User
from repository import inquiry_repo
from schema.inquiry import InquiryCreate, InquiryOut, InquiryStatusUpdate, InquiryTagUpdate, PlanBrief
from service.gym_service import inquiry_tag

router = APIRouter(prefix='/inquiries', tags=['inquiries'])


def _get_inquiry_in_gym(db: Session, inquiry_id: int, gym_id: int) -> Inquiry:
    inquiry = inquiry_repo.get_in_gym(db, inquiry_id, gym_id)
    if inquiry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Inquiry not found')
    return inquiry


def _to_out(inquiry: Inquiry) -> InquiryOut:
    return InquiryOut(
        id=inquiry.id, gym_id=inquiry.gym_id, name=inquiry.name, phone=inquiry.phone,
        email=inquiry.email, note=inquiry.note, status=inquiry.status, plan_id=inquiry.plan_id,
        plan=PlanBrief.model_validate(inquiry.plan) if inquiry.plan else None,
        visit_date=inquiry.visit_date, added_by_id=inquiry.added_by_id,
        added_by_name=inquiry.added_by.get_full_name() if inquiry.added_by else None,
        date_created=inquiry.date_created,
        tag=inquiry_tag(inquiry, date.today()), tag_override=inquiry.tag_override,
    )


@router.get('', response_model=list[InquiryOut])
def list_inquiries(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return [_to_out(i) for i in inquiry_repo.list_for_gym(db, staff.gym_id)]


@router.post('', response_model=InquiryOut, status_code=status.HTTP_201_CREATED)
def add_inquiry(data: InquiryCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    inquiry = Inquiry(
        gym_id=staff.gym_id, added_by_id=staff.id, date_created=date.today(),
        visit_date=data.visit_date or date.today(),
        **data.model_dump(exclude={'visit_date'}),
    )
    return _to_out(inquiry_repo.create(db, inquiry))


@router.post('/{inquiry_id}/status', response_model=InquiryOut)
def set_status(
    inquiry_id: int,
    data: InquiryStatusUpdate,
    db: Session = Depends(get_db),
    staff: User = Depends(require_gym_staff),
):
    inquiry = _get_inquiry_in_gym(db, inquiry_id, staff.gym_id)
    inquiry.status = data.status
    return _to_out(inquiry_repo.save(db, inquiry))


@router.post('/{inquiry_id}/tag', response_model=InquiryOut)
def set_tag(
    inquiry_id: int,
    data: InquiryTagUpdate,
    db: Session = Depends(get_db),
    staff: User = Depends(require_gym_staff),
):
    if data.tag is not None and data.tag not in InquiryTag.ALL:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Invalid tag')
    inquiry = _get_inquiry_in_gym(db, inquiry_id, staff.gym_id)
    inquiry.tag_override = data.tag
    return _to_out(inquiry_repo.save(db, inquiry))


@router.delete('/{inquiry_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_inquiry(inquiry_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    inquiry = _get_inquiry_in_gym(db, inquiry_id, staff.gym_id)
    inquiry_repo.delete(db, inquiry)
