from sqlalchemy.orm import Session

from models.license_key import RegistrationLicenseKey


def get_by_key(db: Session, key: str) -> RegistrationLicenseKey | None:
    """ponytail: reusable by design — same key can register multiple gyms, no is_used check."""
    return db.query(RegistrationLicenseKey).filter(RegistrationLicenseKey.key == key).first()


def create_many(db: Session, count: int) -> list[RegistrationLicenseKey]:
    keys = [RegistrationLicenseKey() for _ in range(count)]
    db.bulk_save_objects(keys)
    db.commit()
    return db.query(RegistrationLicenseKey).order_by(RegistrationLicenseKey.id.desc()).limit(count).all()
