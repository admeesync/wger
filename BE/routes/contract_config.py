from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.contract_option import ContractOption
from models.contract_type import ContractType
from models.user import User
from repository import contract_config_repo
from schema.contract_config import ContractOptionCreate, ContractOptionOut, ContractTypeCreate, ContractTypeOut

router = APIRouter(tags=['contract-config'])


@router.get('/contract-types', response_model=list[ContractTypeOut])
def list_contract_types(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return contract_config_repo.list_types_for_gym(db, staff.gym_id)


@router.post('/contract-types', response_model=ContractTypeOut, status_code=status.HTTP_201_CREATED)
def add_contract_type(data: ContractTypeCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return contract_config_repo.create_type(db, ContractType(gym_id=staff.gym_id, **data.model_dump()))


@router.delete('/contract-types/{type_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_contract_type(type_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    contract_type = contract_config_repo.get_type_in_gym(db, type_id, staff.gym_id)
    if contract_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Contract type not found')
    contract_config_repo.delete_type(db, contract_type)


@router.get('/contract-options', response_model=list[ContractOptionOut])
def list_contract_options(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return contract_config_repo.list_options_for_gym(db, staff.gym_id)


@router.post('/contract-options', response_model=ContractOptionOut, status_code=status.HTTP_201_CREATED)
def add_contract_option(data: ContractOptionCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return contract_config_repo.create_option(db, ContractOption(gym_id=staff.gym_id, **data.model_dump()))


@router.delete('/contract-options/{option_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_contract_option(option_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    option = next((o for o in contract_config_repo.list_options_for_gym(db, staff.gym_id) if o.id == option_id), None)
    if option is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Contract option not found')
    contract_config_repo.delete_option(db, option)
