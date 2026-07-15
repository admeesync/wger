from datetime import date

from pydantic import BaseModel


class InquiryCreate(BaseModel):
    name: str
    phone: str = ''
    note: str = ''


class InquiryOut(InquiryCreate):
    id: int
    gym_id: int
    status: str
    date_created: date

    class Config:
        from_attributes = True


class InquiryStatusUpdate(BaseModel):
    status: str
