import secrets

# ponytail: ambiguous chars (I,1,l,O,0,o) dropped so generated passwords stay readable
_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789'


def generate_password(length: int = 10) -> str:
    return ''.join(secrets.choice(_ALPHABET) for _ in range(length))
