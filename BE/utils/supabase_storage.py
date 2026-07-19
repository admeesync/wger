import requests

from settings.settings import settings


def _object_url(filename: str) -> str:
    return f'{settings.supabase_url}/storage/v1/object/{settings.supabase_storage_bucket}/{filename}'


def _auth_headers() -> dict:
    return {
        'apikey': settings.supabase_service_key,
        'Authorization': f'Bearer {settings.supabase_service_key}',
    }


def upload(filename: str, data: bytes, content_type: str) -> None:
    resp = requests.put(
        _object_url(filename),
        data=data,
        headers={**_auth_headers(), 'Content-Type': content_type, 'x-upsert': 'true'},
        timeout=30,
    )
    resp.raise_for_status()


def delete(filename: str) -> None:
    requests.delete(_object_url(filename), headers=_auth_headers(), timeout=30)


SIGNED_URL_EXPIRY_SECONDS = 3600


def signed_url(filename: str) -> str | None:
    resp = requests.post(
        f'{settings.supabase_url}/storage/v1/object/sign/{settings.supabase_storage_bucket}/{filename}',
        json={'expiresIn': SIGNED_URL_EXPIRY_SECONDS},
        headers=_auth_headers(),
        timeout=30,
    )
    if not resp.ok:
        return None
    return f"{settings.supabase_url}/storage/v1{resp.json()['signedURL']}"
