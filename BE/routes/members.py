from datetime import date, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.contract import Contract
from models.user import User
from repository import contract_repo, member_photo_repo, membership_plan_repo, user_repo
from schema.user import BirthdayOut, MemberCreate, MemberCreated, MemberStatus, UserOut
from service.gym_service import contract_status
from utils.security import hash_password
from utils.passwords import generate_password
from utils.storage import storage_service

router = APIRouter(prefix='/members', tags=['members'])



def _get_member_in_gym(db: Session, member_id: int, gym_id: int) -> User:
    member = user_repo.get_by_id(db, member_id)
    if member is None or member.gym_id != gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    return member


@router.get('', response_model=list[MemberStatus])
def list_members(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    members = user_repo.list_by_gym(db, staff.gym_id)
    contracts = contract_repo.latest_for_members(db, [m.id for m in members])
    today = date.today()
    result = []
    for m in members:
        c = contracts.get(m.id)
        photo = member_photo_repo.get_for_member(db, m.id)
        result.append(MemberStatus(
            id=m.id,
            username=m.username,
            email=m.email,
            status=contract_status(c, today),
            contract_end=c.date_end if c else None,
            contract_amount=str(c.amount) if c else None,
            date_joined=m.date_joined,
            photo_url=storage_service.get_file_url(photo.file_path) if photo else None,
        ))
    return result


@router.get('/birthdays', response_model=list[BirthdayOut])
def birthdays(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    today = date.today()
    members = user_repo.list_by_gym(db, staff.gym_id)
    return [
        BirthdayOut(
            id=m.id, username=m.username, first_name=m.first_name, last_name=m.last_name,
            birthdate=m.birthdate, turning=today.year - m.birthdate.year,
        )
        for m in members
        if m.birthdate and (m.birthdate.month, m.birthdate.day) == (today.month, today.day)
    ]


@router.post('', response_model=MemberCreated, status_code=status.HTTP_201_CREATED)
def add_member(data: MemberCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    if user_repo.get_by_username(db, data.username) or user_repo.get_by_email(db, data.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Username or email already in use')
    password = generate_password()
    member = user_repo.create(
        db,
        User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(password),
            role='member',
            gym_id=staff.gym_id,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            gender=data.gender,
            birthdate=data.birthdate,
        ),
    )

    plan = membership_plan_repo.get_in_gym(db, data.plan_id, staff.gym_id) if data.plan_id else None
    if plan or data.fee_amount or data.date_start:
        start = data.date_start or date.today()
        end = data.date_end or (start + timedelta(days=plan.duration_days) if plan else None)
        amount = data.fee_amount or (str(plan.price) if plan else '0')
        contract_repo.create(db, Contract(member_id=member.id, amount=amount, date_start=start, date_end=end, note=data.notes))

    return MemberCreated(user=member, generated_password=password)


@router.get('/{member_id}', response_model=UserOut)
def get_member(member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return _get_member_in_gym(db, member_id, staff.gym_id)


@router.delete('/{member_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    member = _get_member_in_gym(db, member_id, staff.gym_id)
    user_repo.delete(db, member)


@router.post('/{member_id}/set-device-id', response_model=UserOut)
def set_device_id(
    member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
    device_user_id: str = Body('', embed=True),
):
    member = _get_member_in_gym(db, member_id, staff.gym_id)
    member.device_user_id = device_user_id or None
    db.commit()
    db.refresh(member)
    return member
