from sqlalchemy import Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship

from db.session import Base


class Attendance(Base):
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=False)
    date = Column(Date, nullable=False)
    time_in = Column(Time, nullable=True)
    time_out = Column(Time, nullable=True)
    method = Column(String(10), nullable=False, default='MAN')  # 'BIO' or 'MAN'

    member = relationship('Member')
