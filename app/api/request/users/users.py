from typing import List

from pydantic import BaseModel


class RequestUser(BaseModel):
    id: int
    is_active: bool
    permissions: List[int]


class RequestUpdateUser(BaseModel):
    first_name: str
    last_name: str
