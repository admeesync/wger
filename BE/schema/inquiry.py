from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class InquiryCreate(BaseModel):
    name: str
    phone: str = ''
    email: str = ''
    note: str = ''
    plan_id: int | None = None
    visit_date: date | None = None


class PlanBrief(BaseModel):
    id: int
    name: str
    price: Decimal

    class Config:
        from_attributes = True


class InquiryOut(BaseModel):
    id: int
    gym_id: int
    name: str
    phone: str
    email: str
    note: str
    status: str
    plan_id: int | None
    plan: PlanBrief | None = None
    visit_date: date | None
    added_by_id: int | None
    added_by_name: str | None = None
    date_created: date
    tag: str
    tag_override: str | None

    class Config:
        from_attributes = True


class InquiryStatusUpdate(BaseModel):
    status: str


class InquiryTagUpdate(BaseModel):
    tag: str | None  # 'hot' / 'cool' / 'normal', or null to go back to auto
