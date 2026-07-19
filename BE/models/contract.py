from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Table
from sqlalchemy.orm import relationship

from db.session import Base

contract_options_table = Table(
    'contract_contract_options',
    Base.metadata,
    Column('contract_id', Integer, ForeignKey('contracts.id'), primary_key=True),
    Column('contract_option_id', Integer, ForeignKey('contract_options.id'), primary_key=True),
)


class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    contract_type_id = Column(Integer, ForeignKey('contract_types.id'), nullable=True)
    plan_id = Column(Integer, ForeignKey('membership_plans.id'), nullable=True)
    amount = Column(Numeric(10, 2), default=0)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)
    note = Column(String(500), default='')

    member = relationship('Member')
    contract_type = relationship('ContractType')
    plan = relationship('MembershipPlan')
    options = relationship('ContractOption', secondary=contract_options_table)
