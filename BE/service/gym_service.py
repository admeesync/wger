from datetime import date, timedelta

from models.contract import Contract

EXPIRING_SOON_DAYS = 7


def contract_status(contract: Contract | None, today: date) -> str:
    """Single source of truth for member status, used by dashboard, member list and member detail alike."""
    if contract is None or contract.date_end is None:
        return 'inactive'
    if contract.date_end < today:
        return 'inactive'
    if contract.date_end <= today + timedelta(days=EXPIRING_SOON_DAYS):
        return 'expiring'
    return 'active'
