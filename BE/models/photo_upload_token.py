from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from db.session import Base


class PhotoUploadToken(Base):
    __tablename__ = 'photo_upload_tokens'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    token = Column(String(36), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, nullable=False, default=False)
