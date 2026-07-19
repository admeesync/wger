from sqlalchemy import Column, ForeignKey, Integer, String

from db.session import Base


class ContractType(Base):
    __tablename__ = 'contract_types'

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String(500), default='')
