from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.attendance import Attendance
from models.user import User
from repository import attendance_repo, member_repo
from schema.attendance import AttendanceCreate, AttendanceOut

router = APIRouter(prefix='/attendance', tags=['attendance'])


@router.get('', response_model=list[AttendanceOut])
def list_attendance(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return attendance_repo.list_for_gym(db, staff.gym_id)


@router.post('', response_model=AttendanceOut, status_code=status.HTTP_201_CREATED)
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    staff: User = Depends(require_gym_staff),
):
    member = member_repo.get_by_id(db, data.member_id)
    if member is None or member.gym_id != staff.gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    attendance = Attendance(gym_id=staff.gym_id, **data.model_dump())
    return attendance_repo.create(db, attendance)
