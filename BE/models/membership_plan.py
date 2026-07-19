from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String

from db.session import Base


class MembershipPlan(Base):
    __tablename__ = 'membership_plans'

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey('gyms.id'), nullable=False)
    name = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
