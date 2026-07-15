from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from db.session import Base, engine
from middleware.cors import setup_cors
from routes import attendance, auth, contracts, dashboard, devices, inquiries, license_keys, member_photos, members, plans, profile
from settings.settings import settings

import models  # noqa: F401  registers all models on Base before create_all

app = FastAPI(title='wger-lite API')

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

# Serve frontend static files
app.mount('/', StaticFiles(directory='../FE', html=True), name='frontend')


@app.get('/api/health')
def health():
    return {'status': 'ok'}

