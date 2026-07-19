from datetime import datetime

from pydantic import BaseModel


class DeviceCreate(BaseModel):
    name: str
    corporate_id: str = ''
    api_username: str = ''
    api_password: str = ''
    notes: str = ''


class DeviceUpdate(BaseModel):
    name: str
    corporate_id: str = ''
    api_username: str = ''
    api_password: str | None = None  # blank/None on edit keeps the stored password
    notes: str = ''


class DeviceOut(BaseModel):
    id: int
    gym_id: int
    name: str
    corporate_id: str
    api_username: str
    is_active: bool
    notes: str
    last_sync: datetime | None
    last_sync_count: int | None
    last_sync_display: str

    class Config:
        from_attributes = True
