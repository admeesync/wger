from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str
    license_key: str
    gym_name: str
    first_name: str = ''
    last_name: str = ''


class LoginIn(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
