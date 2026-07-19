from decimal import Decimal

from pydantic import BaseModel


class PlanCreate(BaseModel):
    name: str
    duration_days: int
    price: Decimal


class PlanOut(PlanCreate):
    id: int
    gym_id: int
    is_active: bool

    class Config:
        from_attributes = True
