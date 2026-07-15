from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings.settings import settings


def setup_cors(app: FastAPI) -> None:
    # ponytail: Bearer-token auth (not cookies) is used cross-origin, so credentials
    # mode isn't needed here — that also lets allow_origins stay '*' by default.
    origins = [o.strip() for o in settings.allowed_origins.split(',')]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )
