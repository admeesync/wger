from datetime import date, datetime

from pydantic import BaseModel, EmailStr, field_validator


class GymBrief(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    gym_id: int | None
    gym: GymBrief | None = None
    first_name: str
    last_name: str
    phone: str
    gender: str | None
    birthdate: date | None
    device_user_id: str | None
    date_joined: date

    class Config:
        from_attributes = True

    @field_validator('date_joined', mode='before')
    @classmethod
    def _coerce_date_joined(cls, value):
        return value.date() if isinstance(value, datetime) else value


class MemberOut(BaseModel):
    id: int
    username: str
    email: str
    member_type: str
    gym_id: int | None
    first_name: str
    last_name: str
    phone: str
    gender: str | None
    birthdate: date | None
    device_user_id: str | None
    date_joined: date

    class Config:
        from_attributes = True

    @field_validator('date_joined', mode='before')
    @classmethod
    def _coerce_date_joined(cls, value):
        return value.date() if isinstance(value, datetime) else value


class MemberCreate(BaseModel):
    username: str
    email: EmailStr
    member_type: str = 'member'
    first_name: str = ''
    last_name: str = ''
    phone: str = ''
    gender: str | None = None
    birthdate: date | None = None
    plan_id: int | None = None
    date_start: date | None = None
    date_end: date | None = None
    fee_amount: str | None = None
    notes: str = ''


class MemberUpdate(BaseModel):
    first_name: str = ''
    last_name: str = ''
    email: EmailStr
    phone: str = ''
    gender: str | None = None
    birthdate: date | None = None


class MemberStatus(BaseModel):
    id: int
    username: str
    email: str
    member_type: str
    status: str
    contract_end: date | None
    contract_amount: str | None
    plan_id: int | None = None
    plan_name: str | None = None
    date_joined: date
    photo_url: str | None = None

    @field_validator('date_joined', mode='before')
    @classmethod
    def _coerce_date_joined(cls, value):
        return value.date() if isinstance(value, datetime) else value


class BirthdayOut(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    birthdate: date
    turning: int


class DashboardSummary(BaseModel):
    total_members: int
    today_attendance: int
    expiring_soon: int
    monthly_revenue: str
    new_members_this_month: int
    birthday_count: int
    week_labels: list[str]
    week_data: list[int]
    month_labels: list[str]
    month_data: list[float]
    recent_members: list[MemberOut]
    recent_attendance: list[dict]
