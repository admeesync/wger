from sqlalchemy.orm import Session

from models.contract_option import ContractOption
from models.contract_type import ContractType


def list_types_for_gym(db: Session, gym_id: int) -> list[ContractType]:
    return db.query(ContractType).filter(ContractType.gym_id == gym_id).order_by(ContractType.name).all()


def get_type_in_gym(db: Session, type_id: int, gym_id: int) -> ContractType | None:
    return db.query(ContractType).filter(ContractType.id == type_id, ContractType.gym_id == gym_id).first()


def create_type(db: Session, contract_type: ContractType) -> ContractType:
    db.add(contract_type)
    db.commit()
    db.refresh(contract_type)
    return contract_type


def delete_type(db: Session, contract_type: ContractType) -> None:
    db.delete(contract_type)
    db.commit()


def list_options_for_gym(db: Session, gym_id: int) -> list[ContractOption]:
    return db.query(ContractOption).filter(ContractOption.gym_id == gym_id).order_by(ContractOption.name).all()


def get_options_in_gym(db: Session, option_ids: list[int], gym_id: int) -> list[ContractOption]:
    if not option_ids:
        return []
    return (
        db.query(ContractOption)
        .filter(ContractOption.id.in_(option_ids), ContractOption.gym_id == gym_id)
        .all()
    )


def create_option(db: Session, option: ContractOption) -> ContractOption:
    db.add(option)
    db.commit()
    db.refresh(option)
    return option


def delete_option(db: Session, option: ContractOption) -> None:
    db.delete(option)
    db.commit()
