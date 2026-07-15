from datetime import date, time

from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    member_id: int
    date: date
    time_in: time | None = None


class AttendanceOut(AttendanceCreate):
    id: int
    gym_id: int

    class Config:
        from_attributes = True
