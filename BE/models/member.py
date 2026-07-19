from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String

from db.session import Base


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    member_type = Column(String(20), nullable=False, default='member')  # member, trainer, owner, staff
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=True)
    device_user_id = Column(String(50), nullable=True)
    date_joined = Column(DateTime, nullable=False, default=datetime.utcnow)

    first_name = Column(String(100), default='')
    last_name = Column(String(100), default='')
    phone = Column(String(30), default='')
    gender = Column(String(1), nullable=True)
    birthdate = Column(Date, nullable=True)

    def get_full_name(self) -> str:
        full = f'{self.first_name} {self.last_name}'.strip()
        return full or self.username
