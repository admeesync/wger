from datetime import date, datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
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


class MemberCreated(BaseModel):
    user: UserOut
    generated_password: str


class MemberStatus(BaseModel):
    id: int
    username: str
    email: EmailStr
    status: str
    contract_end: date | None
    contract_amount: str | None
    date_joined: date
    photo_url: str | None = None


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
    recent_members: list[UserOut]
    recent_attendance: list[dict]
