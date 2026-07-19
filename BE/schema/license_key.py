from pydantic import BaseModel


class LicenseKeyOut(BaseModel):
    id: int
    key: str
    is_used: bool

    class Config:
        from_attributes = True
