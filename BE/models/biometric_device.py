from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from db.session import Base


class BiometricDevice(Base):
    __tablename__ = 'biometric_devices'

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=False)
    name = Column(String(100), nullable=False)
    corporate_id = Column(String(100), default='')
    api_username = Column(String(100), default='')
    api_password = Column(String(255), default='')
    is_active = Column(Boolean, nullable=False, default=True)
    notes = Column(String(255), default='')
    last_sync = Column(DateTime, nullable=True)
    last_sync_count = Column(Integer, nullable=True)
