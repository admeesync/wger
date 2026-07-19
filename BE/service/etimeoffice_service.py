import base64
import logging
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests
from sqlalchemy.orm import Session

from models.attendance import Attendance
from models.biometric_device import BiometricDevice
from models.member import Member
from repository import attendance_repo, member_repo

logger = logging.getLogger(__name__)

ETIMEOFFICE_BASE_URL = 'https://api.etimeoffice.com/api/'

# e-TimeOffice machines report punch times in Indian local time regardless of
# where this server runs, since the vendor is India-based.
ETIMEOFFICE_TZ = ZoneInfo('Asia/Kolkata')


class ETimeOfficeError(Exception):
    pass


def _auth_header(device: BiometricDevice) -> str:
    raw = f'{device.corporate_id}:{device.api_username}:{device.api_password}:True'
    encoded = base64.b64encode(raw.encode('utf-8')).decode('ascii')
    return f'Basic {encoded}'


def _fetch_punches(device: BiometricDevice, from_date: datetime, to_date: datetime, empcode: str = 'ALL') -> list[dict]:
    """Calls the e-TimeOffice DownloadPunchDataMCID endpoint. The vendor's
    servers occasionally return a transient 500 with no request-side cause,
    so failed attempts are retried a couple of times before giving up."""
    params = {
        'Empcode': empcode,
        'FromDate': from_date.strftime('%d/%m/%Y_%H:%M'),
        'ToDate': to_date.strftime('%d/%m/%Y_%H:%M'),
    }
    headers = {'Authorization': _auth_header(device), 'Content-Type': 'application/json'}

    attempts = 3
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(
                ETIMEOFFICE_BASE_URL + 'DownloadPunchDataMCID', params=params, headers=headers, timeout=30,
            )
            if response.status_code >= 500 and attempt < attempts:
                time.sleep(1.5 * attempt)
                continue
            response.raise_for_status()
            data = response.json()
            if data.get('Error'):
                raise ETimeOfficeError(data.get('Msg', 'e-TimeOffice API returned an error'))
            return data.get('PunchData', [])
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < attempts:
                time.sleep(1.5 * attempt)
                continue
            raise ETimeOfficeError(f'Could not reach e-TimeOffice API: {exc}') from exc

    raise ETimeOfficeError(str(last_exc))


def _get_or_create_member(db: Session, gym_id: int, empcode: str, name: str | None) -> Member:
    """Finds the member matching a machine Empcode within this gym, or
    auto-creates one (this is how members enrolled on the biometric machine
    end up in wger-app automatically)."""
    existing = member_repo.get_by_device_user_id(db, gym_id, empcode)
    if existing:
        return existing

    # Namespaced by gym so the same Empcode on two different gyms' machines
    # can't collide on the globally-unique username.
    username = f'gym{gym_id}_machine_{empcode}'
    existing = member_repo.get_by_username(db, username)
    if existing:
        return existing

    display_name = (name or '').strip() or f'Member {empcode}'
    first_name, _, last_name = display_name.partition(' ')

    return member_repo.create(db, Member(
        username=username, email=f'{username}@device.local',
        gym_id=gym_id, first_name=first_name, last_name=last_name,
        device_user_id=empcode,
    ))


def sync_device(db: Session, device: BiometricDevice) -> tuple[str, int]:
    """Pulls punch data from the e-TimeOffice cloud API, auto-creates any gym
    member that doesn't exist yet (matched/created by machine Empcode), and
    saves the punches as Attendance records. Raises ETimeOfficeError on
    failure. Returns (message, saved_count)."""
    now_ist = datetime.now(ETIMEOFFICE_TZ)
    # last_sync is stored as a naive UTC datetime (this codebase's convention,
    # e.g. datetime.utcnow()) - it must be tagged UTC before converting to IST,
    # otherwise astimezone() would wrongly assume the server's local timezone.
    from_date = (
        device.last_sync.replace(tzinfo=timezone.utc).astimezone(ETIMEOFFICE_TZ)
        if device.last_sync else now_ist - timedelta(days=30)
    )
    # Forward buffer since the vendor's server clock has been observed to
    # drift several hours ahead of real time - too small a buffer silently
    # excludes recent punches that are timestamped "in the future".
    to_date = now_ist + timedelta(hours=12)

    punches = _fetch_punches(device, from_date, to_date)

    # Group punches per member per day - only the earliest punch of the day
    # is kept as time_in. time_out is intentionally not tracked from
    # e-TimeOffice punches.
    punches_by_day: dict[tuple[int, object], list] = {}
    seen_empcodes = set()
    for punch in punches:
        empcode = punch.get('Empcode')
        if not empcode:
            continue
        try:
            punch_dt = datetime.strptime(punch['PunchDate'], '%d/%m/%Y %H:%M:%S')
        except (KeyError, ValueError):
            continue

        member = _get_or_create_member(db, device.gym_id, empcode, punch.get('Name'))
        seen_empcodes.add(empcode)
        key = (member.id, punch_dt.date())
        punches_by_day.setdefault(key, []).append(punch_dt.time())

    # Only touch the DB (and count it as "saved") when the punch is actually
    # new or changed, so a punch whose timestamp drifts into "the future"
    # (vendor clock drift) doesn't get reported as newly synced every run.
    saved = 0
    for (member_id, day), times in punches_by_day.items():
        time_in = min(times)
        existing = attendance_repo.get_for_member_on_date(db, member_id, day)
        if existing and existing.time_in == time_in:
            continue
        if existing:
            existing.time_in = time_in
            existing.method = 'BIO'
            attendance_repo.save(db, existing)
        else:
            attendance_repo.create(db, Attendance(
                gym_id=device.gym_id, member_id=member_id, date=day, time_in=time_in, method='BIO',
            ))
        saved += 1

    device.last_sync = datetime.utcnow()
    device.last_sync_count = saved
    db.commit()

    msg = f'Sync complete — {saved} attendance record(s) updated, {len(seen_empcodes)} member(s) seen.'
    logger.info('e-TimeOffice sync: device=%s, saved=%d', device.name, saved)
    return msg, saved
