from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from db.session import Base


class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Numeric(10, 2), default=0)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)
    note = Column(String(500), default='')

    member = relationship('User')
