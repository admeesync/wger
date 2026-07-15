from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.contract import Contract
from models.user import User
from repository import contract_repo, user_repo
from schema.contract import ContractCreate, ContractOut, ContractWithMemberOut
from service.gym_service import contract_status

router = APIRouter(prefix='/members/{member_id}/contracts', tags=['contracts'])
gym_contracts_router = APIRouter(prefix='/contracts', tags=['contracts'])


@gym_contracts_router.get('', response_model=list[ContractWithMemberOut])
def list_gym_contracts(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    today = date.today()
    contracts = contract_repo.list_for_gym(db, staff.gym_id)
    members = {m.id: m for m in user_repo.list_by_gym(db, staff.gym_id)}
    result = []
    for c in contracts:
        member = members.get(c.member_id)
        if member is None:
            continue
        result.append(ContractWithMemberOut(
            id=c.id, member_id=c.member_id, amount=c.amount, date_start=c.date_start,
            date_end=c.date_end, note=c.note, member_username=member.username,
            is_active=(c.date_end is None or c.date_end >= today),
            status=contract_status(c, today),
        ))
    return result


def _member_in_gym(db: Session, member_id: int, gym_id: int):
    member = user_repo.get_by_id(db, member_id)
    if member is None or member.gym_id != gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    return member


@router.get('', response_model=list[ContractOut])
def list_contracts(member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    _member_in_gym(db, member_id, staff.gym_id)
    return contract_repo.list_for_member(db, member_id)


@router.post('', response_model=ContractOut, status_code=status.HTTP_201_CREATED)
def add_contract(
    member_id: int,
    data: ContractCreate,
    db: Session = Depends(get_db),
    staff: User = Depends(require_gym_staff),
):
    _member_in_gym(db, member_id, staff.gym_id)
    contract = Contract(member_id=member_id, **data.model_dump(exclude={'member_id'}))
    return contract_repo.create(db, contract)
