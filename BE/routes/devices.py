from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.auth import require_gym_staff
from dependencies.db import get_db
from models.biometric_device import BiometricDevice
from models.user import User
from repository import biometric_repo
from schema.biometric_device import DeviceCreate, DeviceOut, DeviceUpdate
from service import biometric_service
from service.etimeoffice_service import ETimeOfficeError

router = APIRouter(prefix='/devices', tags=['devices'])


def _humanize(last_sync: datetime | None) -> str:
    if last_sync is None:
        return 'Never synced'
    delta = datetime.utcnow() - last_sync
    seconds = delta.total_seconds()
    if seconds < 60:
        return 'Just now'
    if seconds < 3600:
        return f'{int(seconds // 60)} min ago'
    if seconds < 86400:
        return f'{int(seconds // 3600)} hour(s) ago'
    return f'{int(seconds // 86400)} day(s) ago'


def _to_out(device: BiometricDevice) -> DeviceOut:
    return DeviceOut(
        id=device.id, gym_id=device.gym_id, name=device.name, corporate_id=device.corporate_id,
        api_username=device.api_username, is_active=device.is_active, notes=device.notes,
        last_sync=device.last_sync, last_sync_count=device.last_sync_count,
        last_sync_display=_humanize(device.last_sync),
    )


def _get_device_in_gym(db: Session, device_id: int, gym_id: int) -> BiometricDevice:
    device = biometric_repo.get_in_gym(db, device_id, gym_id)
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Device not found')
    return device


@router.get('', response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    return [_to_out(d) for d in biometric_repo.list_for_gym(db, staff.gym_id)]


@router.post('', response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
def add_device(data: DeviceCreate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    device = BiometricDevice(gym_id=staff.gym_id, **data.model_dump())
    device = biometric_repo.create(db, device)
    try:
        biometric_service.sync_device(db, device)
    except ETimeOfficeError:
        pass  # device is created either way; the dedicated Sync button surfaces the real error
    return _to_out(biometric_repo.save(db, device))


@router.put('/{device_id}', response_model=DeviceOut)
def update_device(
    device_id: int, data: DeviceUpdate, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff),
):
    device = _get_device_in_gym(db, device_id, staff.gym_id)
    device.name = data.name
    device.corporate_id = data.corporate_id
    device.api_username = data.api_username
    device.notes = data.notes
    if data.api_password:
        device.api_password = data.api_password
    return _to_out(biometric_repo.save(db, device))


@router.post('/{device_id}/toggle', response_model=DeviceOut)
def toggle_device(device_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    device = _get_device_in_gym(db, device_id, staff.gym_id)
    device.is_active = not device.is_active
    return _to_out(biometric_repo.save(db, device))


@router.delete('/{device_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    device = _get_device_in_gym(db, device_id, staff.gym_id)
    biometric_repo.delete(db, device)


@router.post('/{device_id}/sync', response_model=DeviceOut)
def sync_device(device_id: int, db: Session = Depends(get_db), staff: User = Depends(require_gym_staff)):
    device = _get_device_in_gym(db, device_id, staff.gym_id)
    try:
        biometric_service.sync_device(db, device)
    except ETimeOfficeError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc
    return _to_out(biometric_repo.save(db, device))
