from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ContractCreate(BaseModel):
    member_id: int
    amount: Decimal
    date_start: date
    date_end: date | None = None
    note: str = ''


class ContractOut(BaseModel):
    id: int
    member_id: int
    amount: Decimal
    date_start: date
    date_end: date | None
    note: str

    class Config:
        from_attributes = True


class ContractWithMemberOut(ContractOut):
    member_username: str
    is_active: bool
    status: str
