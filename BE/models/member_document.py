from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from db.session import Base


class MemberDocument(Base):
    __tablename__ = 'member_documents'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
