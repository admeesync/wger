from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.user import User
from repository import attendance_repo, contract_repo, gym_repo, user_repo
from schema.gym import ProfileOut, ProfileUpdate

router = APIRouter(prefix='/profile', tags=['profile'])


@router.get('', response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    today = date.today()
    members = user_repo.list_by_gym(db, staff.gym_id)
    contracts = contract_repo.list_for_gym(db, staff.gym_id)
    active_contracts = sum(1 for c in contracts if c.date_end is None or c.date_end >= today)
    today_checkins = len(attendance_repo.list_for_gym_on_date(db, staff.gym_id, today))

    return ProfileOut(
        first_name=staff.first_name, last_name=staff.last_name, username=staff.username,
        email=staff.email, role=staff.role, date_joined=staff.date_joined.date().isoformat(),
        gym=staff.gym, total_members=len(members), active_contracts=active_contracts,
        today_checkins=today_checkins,
    )


@router.post('', response_model=ProfileOut)
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    staff.first_name = data.first_name
    staff.last_name = data.last_name
    if data.email:
        staff.email = data.email
    db.commit()

    gym = gym_repo.get_by_id(db, staff.gym_id)
    if gym:
        gym.name = data.gym_name or gym.name
        gym.phone = data.gym_phone
        gym.email = data.gym_email
        gym.owner = data.gym_owner
        gym.street = data.gym_street
        gym.city = data.gym_city
        gym.zip_code = data.gym_zip
        gym.drive_folder_id = data.drive_folder_id
        db.commit()

    return get_profile(db, staff)
