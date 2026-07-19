from pydantic import BaseModel


class ContractTypeCreate(BaseModel):
    name: str
    description: str = ''


class ContractTypeOut(ContractTypeCreate):
    id: int
    gym_id: int

    class Config:
        from_attributes = True


class ContractOptionCreate(BaseModel):
    name: str
    description: str = ''


class ContractOptionOut(ContractOptionCreate):
    id: int
    gym_id: int

    class Config:
        from_attributes = True
