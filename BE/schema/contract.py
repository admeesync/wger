from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from schema.inquiry import PlanBrief


class ContractTypeBrief(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ContractOptionBrief(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    member_id: int
    amount: Decimal
    date_start: date
    date_end: date | None = None
    note: str = ''
    contract_type_id: int | None = None
    plan_id: int | None = None
    option_ids: list[int] = []


class ContractOut(BaseModel):
    id: int
    member_id: int
    amount: Decimal
    date_start: date
    date_end: date | None
    note: str
    contract_type: ContractTypeBrief | None = None
    plan: PlanBrief | None = None
    options: list[ContractOptionBrief] = []

    class Config:
        from_attributes = True


class ContractWithMemberOut(ContractOut):
    member_username: str
    is_active: bool
    status: str
