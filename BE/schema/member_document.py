from datetime import datetime

from pydantic import BaseModel


class MemberDocumentOut(BaseModel):
    id: int
    member_id: int
    file_path: str
    original_name: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
