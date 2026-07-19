import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.session import Base


class RegistrationLicenseKey(Base):
    __tablename__ = 'registration_license_keys'

    id = Column(Integer, primary_key=True)
    key = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    is_used = Column(Boolean, default=False, nullable=False)
    used_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    used_at = Column(DateTime, nullable=True)

    used_by = relationship('User')
