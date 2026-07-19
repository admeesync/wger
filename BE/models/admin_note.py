from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.session import Base


class AdminNote(Base):
    __tablename__ = 'admin_notes'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    note = Column(String(2000), nullable=False)
    created_at = Column(DateTime, nullable=False)

    author = relationship('User', foreign_keys=[author_id])
