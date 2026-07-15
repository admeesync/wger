"""Run once after first install: creates uploads/ dir, tables, and a super-admin + one license key."""
import os

from db.session import Base, SessionLocal, engine
from models.license_key import RegistrationLicenseKey
from models.user import User
from settings.settings import settings
from utils.security import hash_password

import models  # noqa: F401

os.makedirs(settings.upload_dir, exist_ok=True)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    if not db.query(User).filter(User.username == 'superadmin').first():
        db.add(
            User(
                username='superadmin',
                email='superadmin@example.com',
                hashed_password=hash_password('changeme123'),
                role='super_admin',
            )
        )
    key = db.query(RegistrationLicenseKey).filter(RegistrationLicenseKey.is_used.is_(False)).first()
    if key is None:
        key = RegistrationLicenseKey()
        db.add(key)
    db.commit()
    db.refresh(key)
    print('superadmin / changeme123')
    print('license key for first gym-admin registration:', key.key)
finally:
    db.close()
