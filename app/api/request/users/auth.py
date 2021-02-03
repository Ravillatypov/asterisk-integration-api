import jwt
from pydantic import BaseModel, Field, validator

from app.config import app_config


class RequestAuth(BaseModel):
    username: str
    password: str


class RequestRegister(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=4)
    first_name: str
    last_name: str

    @validator('username', pre=True, always=True)
    def _username(cls, v: str):
        v = v.strip()
        assert v.isalnum(), 'must be alphanumeric'
        return v


class RequestRefreshToken(BaseModel):
    refresh_token: str

    @validator('refresh_token', pre=True)
    def _validate(cls, val: str) -> str:
        try:
            jwt.decode(val, app_config.jwt.sig)
        except jwt.ExpiredSignatureError:
            raise ValueError('token is expired')
        except jwt.InvalidSignatureError:
            raise ValueError('sign check failed')
        except Exception:
            raise ValueError('Is not JWT token')
        return val


class RequestRevokeToken(BaseModel):
    refresh_token: str


class RequestAuthByToken(BaseModel):
    token: str = Field(min_length=5)
