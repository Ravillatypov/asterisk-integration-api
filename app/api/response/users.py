from typing import List

from pydantic import BaseModel


class ResponseUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    permissions: List[int]
    username: str
    is_active: bool
    company_id: int

    class Config:
        orm_mode = True


class ResponseUsers(BaseModel):
    result: List[ResponseUser]

    def __init__(self, result, *args, **kwargs):
        super(ResponseUsers, self).__init__(*args, result=[ResponseUser.from_orm(i) for i in result], **kwargs)


class ResponseRefreshAccessToken(BaseModel):
    refresh_token: str
    access_token: str

    class Config:
        orm_mode = True


class ResponseUserWithTokens(ResponseUser, ResponseRefreshAccessToken):
    pass
