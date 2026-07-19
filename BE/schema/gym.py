from pydantic import BaseModel


class GymOut(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    address: str
    owner: str
    street: str
    city: str
    zip_code: str
    drive_folder_id: str

    class Config:
        from_attributes = True


class ProfileOut(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    role: str
    date_joined: str
    gym: GymOut | None
    total_members: int
    active_contracts: int
    today_checkins: int


class ProfileUpdate(BaseModel):
    first_name: str = ''
    last_name: str = ''
    email: str = ''
    gym_name: str = ''
    gym_phone: str = ''
    gym_email: str = ''
    gym_owner: str = ''
    gym_street: str = ''
    gym_city: str = ''
    gym_zip: str = ''
    drive_folder_id: str = ''
