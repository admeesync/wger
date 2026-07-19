from sqlalchemy.orm import Session

from models.biometric_device import BiometricDevice


def list_for_gym(db: Session, gym_id: int) -> list[BiometricDevice]:
    return db.query(BiometricDevice).filter(BiometricDevice.gym_id == gym_id).all()


def list_all_active(db: Session) -> list[BiometricDevice]:
    return db.query(BiometricDevice).filter(BiometricDevice.is_active.is_(True)).all()


def get_in_gym(db: Session, device_id: int, gym_id: int) -> BiometricDevice | None:
    return (
        db.query(BiometricDevice)
        .filter(BiometricDevice.id == device_id, BiometricDevice.gym_id == gym_id)
        .first()
    )


def create(db: Session, device: BiometricDevice) -> BiometricDevice:
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def save(db: Session, device: BiometricDevice) -> BiometricDevice:
    db.commit()
    db.refresh(device)
    return device


def delete(db: Session, device: BiometricDevice) -> None:
    db.delete(device)
    db.commit()
