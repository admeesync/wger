from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.membership_plan import MembershipPlan
from models.user import User
from repository import membership_plan_repo
from schema.membership_plan import PlanCreate, PlanOut

router = APIRouter(prefix='/plans', tags=['plans'])


def _get_plan_in_gym(db: Session, plan_id: int, gym_id: int) -> MembershipPlan:
    plan = membership_plan_repo.get_in_gym(db, plan_id, gym_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Plan not found')
    return plan


@router.get('', response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return membership_plan_repo.list_for_gym(db, staff.gym_id)


@router.post('', response_model=PlanOut, status_code=status.HTTP_201_CREATED)
def add_plan(data: PlanCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    plan = MembershipPlan(gym_id=staff.gym_id, **data.model_dump())
    return membership_plan_repo.create(db, plan)


@router.post('/{plan_id}/toggle', response_model=PlanOut)
def toggle_plan(plan_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    plan = _get_plan_in_gym(db, plan_id, staff.gym_id)
    plan.is_active = not plan.is_active
    return membership_plan_repo.save(db, plan)


@router.delete('/{plan_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    plan = _get_plan_in_gym(db, plan_id, staff.gym_id)
    membership_plan_repo.delete(db, plan)
