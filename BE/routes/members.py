import csv
import io
import os
from datetime import date, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from config.constants import MemberType
from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.admin_note import AdminNote
from models.attendance import Attendance
from models.contract import Contract, contract_options_table
from models.member import Member
from models.member_document import MemberDocument
from models.member_photo import MemberPhoto
from models.photo_upload_token import PhotoUploadToken
from models.user import User
from repository import attendance_repo, contract_repo, member_document_repo, member_photo_repo, member_repo, membership_plan_repo
from schema.user import BirthdayOut, MemberCreate, MemberOut, MemberStatus, MemberUpdate
from service.gym_service import contract_status
from settings.settings import settings
from utils import supabase_storage

router = APIRouter(prefix='/members', tags=['members'])


def _get_member_in_gym(db: Session, member_id: int, gym_id: int) -> Member:
    member = member_repo.get_by_id(db, member_id)
    if member is None or member.gym_id != gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    return member


@router.get('', response_model=list[MemberStatus])
def list_members(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    members = member_repo.list_by_gym(db, staff.gym_id)
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
            member_type=m.member_type,
            status=contract_status(c, today),
            contract_end=c.date_end if c else None,
            contract_amount=str(c.amount) if c else None,
            plan_id=c.plan_id if c else None,
            plan_name=c.plan.name if c and c.plan else None,
            date_joined=m.date_joined,
            photo_url=supabase_storage.signed_url(photo.file_path) if photo else None,
        ))
    return result


@router.get('/birthdays', response_model=list[BirthdayOut])
def birthdays(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    today = date.today()
    members = member_repo.list_by_gym(db, staff.gym_id)
    return [
        BirthdayOut(
            id=m.id, username=m.username, first_name=m.first_name, last_name=m.last_name,
            birthdate=m.birthdate, turning=today.year - m.birthdate.year,
        )
        for m in members
        if m.birthdate and (m.birthdate.month, m.birthdate.day) == (today.month, today.day)
    ]


@router.get('/export')
def export_members(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    members = member_repo.list_by_gym(db, staff.gym_id)
    contracts = contract_repo.latest_for_members(db, [m.id for m in members])
    today = date.today()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['Username', 'First Name', 'Last Name', 'Email', 'Phone', 'Status', 'Contract End', 'Date Joined'])
    for m in members:
        c = contracts.get(m.id)
        writer.writerow([
            m.username, m.first_name, m.last_name, m.email, m.phone,
            contract_status(c, today), c.date_end if c else '', m.date_joined,
        ])
    return Response(
        content=buf.getvalue(), media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="members.csv"'},
    )


@router.post('', response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def add_member(data: MemberCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    if data.member_type not in MemberType.ALL:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Invalid member type')
    if data.member_type == MemberType.OWNER and member_repo.get_owner_in_gym(db, staff.gym_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'This gym already has an owner')
    if member_repo.get_by_username(db, data.username) or member_repo.get_by_email(db, data.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Username or email already in use')
    member = member_repo.create(
        db,
        Member(
            username=data.username,
            email=data.email,
            member_type=data.member_type,
            gym_id=staff.gym_id,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            gender=data.gender,
            birthdate=data.birthdate,
        ),
    )

    # Fees/membership plans only apply to actual paying members — trainers,
    # the owner, and other staff tags never get a contract.
    if data.member_type == MemberType.MEMBER:
        plan = membership_plan_repo.get_in_gym(db, data.plan_id, staff.gym_id) if data.plan_id else None
        if plan or data.fee_amount or data.date_start:
            start = data.date_start or date.today()
            end = data.date_end or (start + timedelta(days=plan.duration_days) if plan else None)
            amount = data.fee_amount or (str(plan.price) if plan else '0')
            contract_repo.create(db, Contract(
                member_id=member.id, plan_id=plan.id if plan else None,
                amount=amount, date_start=start, date_end=end, note=data.notes,
            ))

    return member


@router.get('/{member_id}', response_model=MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return _get_member_in_gym(db, member_id, staff.gym_id)


@router.put('/{member_id}', response_model=MemberOut)
def update_member(
    member_id: int, data: MemberUpdate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
):
    member = _get_member_in_gym(db, member_id, staff.gym_id)
    existing = member_repo.get_by_email(db, data.email)
    if existing and existing.id != member.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Email already in use')
    member.first_name = data.first_name
    member.last_name = data.last_name
    member.email = data.email
    member.phone = data.phone
    member.gender = data.gender
    member.birthdate = data.birthdate
    db.commit()
    db.refresh(member)
    return member


def _delete_member_files_and_records(db: Session, member_id: int) -> None:
    photo = member_photo_repo.get_for_member(db, member_id)
    if photo:
        supabase_storage.delete(photo.file_path)
    for document in member_document_repo.list_for_member(db, member_id):
        path = os.path.join(settings.upload_dir, document.file_path)
        if os.path.exists(path):
            os.remove(path)

    contract_ids = [c.id for c in contract_repo.list_for_member(db, member_id)]
    if contract_ids:
        db.execute(contract_options_table.delete().where(contract_options_table.c.contract_id.in_(contract_ids)))
    db.query(Contract).filter(Contract.member_id == member_id).delete()
    db.query(AdminNote).filter(AdminNote.member_id == member_id).delete()
    db.query(MemberDocument).filter(MemberDocument.member_id == member_id).delete()
    db.query(PhotoUploadToken).filter(PhotoUploadToken.member_id == member_id).delete()
    db.query(MemberPhoto).filter(MemberPhoto.member_id == member_id).delete()


@router.delete('/{member_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    member = _get_member_in_gym(db, member_id, staff.gym_id)
    _delete_member_files_and_records(db, member_id)
    db.query(Attendance).filter(Attendance.member_id == member_id).delete()
    db.commit()

    member_repo.delete(db, member)


def _absorb_duplicate(db: Session, duplicate: Member, target: Member) -> None:
    """A biometric sync auto-creates a placeholder member before it's linked
    to the real one. Once the real member claims that Empcode, fold the
    placeholder's attendance into it (skipping dates the target already has,
    so a manual entry isn't clobbered) and remove the placeholder."""
    for punch in db.query(Attendance).filter(Attendance.member_id == duplicate.id):
        if attendance_repo.get_for_member_on_date(db, target.id, punch.date):
            db.delete(punch)
        else:
            punch.member_id = target.id
    _delete_member_files_and_records(db, duplicate.id)
    db.commit()
    member_repo.delete(db, duplicate)


@router.post('/{member_id}/set-device-id', response_model=MemberOut)
def set_device_id(
    member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
    device_user_id: str = Body('', embed=True),
):
    member = _get_member_in_gym(db, member_id, staff.gym_id)
    device_user_id = device_user_id or None

    if device_user_id:
        duplicate = member_repo.get_by_device_user_id(db, staff.gym_id, device_user_id)
        if duplicate and duplicate.id != member.id:
            # A biometric sync names its placeholder members this way (see
            # etimeoffice_service._get_or_create_member) - that's the only
            # case where auto-absorbing the duplicate is safe. Anything else
            # means this Device ID is already claimed by a real member.
            placeholder_username = f'gym{staff.gym_id}_machine_{device_user_id}'
            if duplicate.username != placeholder_username:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    f'Device ID "{device_user_id}" is already assigned to {duplicate.get_full_name()}.',
                )
            _absorb_duplicate(db, duplicate, member)

    member.device_user_id = device_user_id
    db.commit()
    db.refresh(member)
    return member
