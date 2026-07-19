import asyncio
import contextlib
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from db.session import Base, engine
from middleware.cors import setup_cors
from routes import admin_notes, attendance, auth, contract_config, contracts, dashboard, devices, inquiries, license_keys, member_documents, member_photos, members, plans, profile
from service.biometric_service import sync_all_active_devices
from settings.settings import settings

import models  # noqa: F401  registers all models on Base before create_all

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

AUTO_SYNC_INTERVAL_SECONDS = 1 * 60


async def _auto_sync_loop():
    while True:
        await asyncio.sleep(AUTO_SYNC_INTERVAL_SECONDS)
        try:
            await asyncio.to_thread(sync_all_active_devices)
        except Exception:
            logger.exception('Biometric auto-sync loop failed')


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_auto_sync_loop())
    yield
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


app = FastAPI(title='wger-lite API', lifespan=lifespan)

setup_cors(app)
Base.metadata.create_all(bind=engine)
app.mount('/uploads', StaticFiles(directory=settings.upload_dir), name='uploads')

app.include_router(auth.router, prefix='/api')
app.include_router(dashboard.router, prefix='/api')
app.include_router(members.router, prefix='/api')
app.include_router(contracts.router, prefix='/api')
app.include_router(contracts.gym_contracts_router, prefix='/api')
app.include_router(profile.router, prefix='/api')
app.include_router(plans.router, prefix='/api')
app.include_router(attendance.router, prefix='/api')
app.include_router(inquiries.router, prefix='/api')
app.include_router(devices.router, prefix='/api')
app.include_router(member_photos.router, prefix='/api')
app.include_router(license_keys.router, prefix='/api')
app.include_router(admin_notes.router, prefix='/api')
app.include_router(member_documents.router, prefix='/api')
app.include_router(member_photos.public_router, prefix='/api')
app.include_router(contract_config.router, prefix='/api')


@app.get('/api/health')
def health():
    return {'status': 'ok'}


import os
# Mount frontend files at the root
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../FE'))
if os.path.exists(frontend_dir):
    app.mount('/', StaticFiles(directory=frontend_dir, html=True), name='frontend')
