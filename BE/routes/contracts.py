from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.contract import Contract
from models.user import User
from repository import contract_config_repo, contract_repo, member_repo
from schema.contract import ContractCreate, ContractOut, ContractWithMemberOut
from service import contract_pdf_service
from service.gym_service import contract_status

router = APIRouter(prefix='/members/{member_id}/contracts', tags=['contracts'])
gym_contracts_router = APIRouter(prefix='/contracts', tags=['contracts'])


def _to_out(c: Contract) -> ContractOut:
    return ContractOut.model_validate(c)


@gym_contracts_router.get('', response_model=list[ContractWithMemberOut])
def list_gym_contracts(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    today = date.today()
    contracts = contract_repo.list_for_gym(db, staff.gym_id)
    members = {m.id: m for m in member_repo.list_by_gym(db, staff.gym_id)}
    result = []
    for c in contracts:
        member = members.get(c.member_id)
        if member is None:
            continue
        out = _to_out(c)
        result.append(ContractWithMemberOut(
            **out.model_dump(), member_username=member.username,
            is_active=(c.date_end is None or c.date_end >= today),
            status=contract_status(c, today),
        ))
    return result


def _member_in_gym(db: Session, member_id: int, gym_id: int):
    member = member_repo.get_by_id(db, member_id)
    if member is None or member.gym_id != gym_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Member not found')
    return member


def _get_contract_in_gym(db: Session, contract_id: int, member_id: int, gym_id: int) -> Contract:
    _member_in_gym(db, member_id, gym_id)
    contract = next((c for c in contract_repo.list_for_member(db, member_id) if c.id == contract_id), None)
    if contract is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Contract not found')
    return contract


@router.get('', response_model=list[ContractOut])
def list_contracts(member_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    _member_in_gym(db, member_id, staff.gym_id)
    return [_to_out(c) for c in contract_repo.list_for_member(db, member_id)]


@router.post('', response_model=ContractOut, status_code=status.HTTP_201_CREATED)
def add_contract(
    member_id: int,
    data: ContractCreate,
    db: Session = Depends(get_db),
    staff: User = Depends(require_gym_staff),
):
    _member_in_gym(db, member_id, staff.gym_id)
    fields = data.model_dump(exclude={'member_id', 'option_ids'})
    contract = Contract(member_id=member_id, **fields)
    contract.options = contract_config_repo.get_options_in_gym(db, data.option_ids, staff.gym_id)
    return _to_out(contract_repo.create(db, contract))


@router.get('/{contract_id}/pdf')
def download_contract_pdf(
    member_id: int, contract_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
):
    contract = _get_contract_in_gym(db, contract_id, member_id, staff.gym_id)
    pdf_bytes = contract_pdf_service.generate_contract_pdf(contract, staff.gym.name if staff.gym else 'Gym')
    return Response(
        content=pdf_bytes, media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="contract-{contract.id}.pdf"'},
    )
