from datetime import date, timedelta

from models.contract import Contract
from models.inquiry import Inquiry

EXPIRING_SOON_DAYS = 7
INQUIRY_COOL_AFTER_DAYS = 7
INQUIRY_NORMAL_AFTER_DAYS = 12


def contract_status(contract: Contract | None, today: date) -> str:
    """Single source of truth for member status, used by dashboard, member list and member detail alike."""
    if contract is None or contract.date_end is None:
        return 'inactive'
    if contract.date_end < today:
        return 'inactive'
    if contract.date_end <= today + timedelta(days=EXPIRING_SOON_DAYS):
        return 'expiring'
    return 'active'


def inquiry_tag(inquiry: Inquiry, today: date) -> str:
    """A manually-set tag always wins; otherwise the tag is derived from lead age."""
    if inquiry.tag_override:
        return inquiry.tag_override
    age_days = (today - inquiry.date_created).days
    if age_days >= INQUIRY_NORMAL_AFTER_DAYS:
        return 'normal'
    if age_days >= INQUIRY_COOL_AFTER_DAYS:
        return 'cool'
    return 'hot'
