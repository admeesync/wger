from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.session import Base


class Inquiry(Base):
    __tablename__ = 'inquiries'

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(30), default='')
    email = Column(String(255), default='')
    note = Column(String(500), default='')
    status = Column(String(20), nullable=False, default='new')
    plan_id = Column(Integer, ForeignKey('membership_plans.id'), nullable=True)
    visit_date = Column(Date, nullable=True)
    added_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    date_created = Column(Date, nullable=False)
    tag_override = Column(String(10), nullable=True)  # 'hot'/'cool'/'normal', or null for auto (by lead age)

    plan = relationship('MembershipPlan')
    added_by = relationship('User')
