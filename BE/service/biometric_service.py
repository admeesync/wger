import logging

from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.biometric_device import BiometricDevice
from repository import biometric_repo
from service import etimeoffice_service
from service.etimeoffice_service import ETimeOfficeError

logger = logging.getLogger(__name__)


def sync_device(db: Session, device: BiometricDevice) -> str:
    """Pulls real attendance punches from the device's e-TimeOffice account.
    Raises ETimeOfficeError (with a user-facing message) on failure."""
    msg, _count = etimeoffice_service.sync_device(db, device)
    return msg


def sync_all_active_devices() -> None:
    """Runs on a timer (see main.py) so gyms don't have to remember to click
    Sync themselves. One device failing (bad creds, e-TimeOffice down) must
    not stop the others from syncing."""
    db = SessionLocal()
    try:
        for device in biometric_repo.list_all_active(db):
            try:
                sync_device(db, device)
            except ETimeOfficeError as exc:
                logger.warning('Auto-sync failed for device=%s: %s', device.name, exc)
    finally:
        db.close()
