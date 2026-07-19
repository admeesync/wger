from datetime import datetime

from pydantic import BaseModel


class AdminNoteCreate(BaseModel):
    note: str


class AdminNoteOut(BaseModel):
    id: int
    member_id: int
    author_id: int | None
    author_name: str | None = None
    note: str
    created_at: datetime

    class Config:
        from_attributes = True
