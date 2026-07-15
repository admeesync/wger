from sqlalchemy import Column, Integer, String

from db.session import Base


class Gym(Base):
    __tablename__ = 'gyms'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(30), default='')
    email = Column(String(255), default='')
    address = Column(String(255), default='')
    owner = Column(String(100), default='')
    street = Column(String(150), default='')
    city = Column(String(100), default='')
    zip_code = Column(String(20), default='')
    drive_folder_id = Column(String(255), default='')
