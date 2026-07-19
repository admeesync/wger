from sqlalchemy import Column, ForeignKey, Integer, String

from db.session import Base


class MemberPhoto(Base):
    __tablename__ = 'member_photos'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), unique=True, nullable=False)
    file_path = Column(String(255), nullable=False)
