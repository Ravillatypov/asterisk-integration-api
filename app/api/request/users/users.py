from typing import List

from pydantic import BaseModel, Field


class RequestUser(BaseModel):
    id: int
    is_active: bool
    permissions: List[int]
    password: str = Field(None, min_length=4)


class RequestUpdateUser(BaseModel):
    first_name: str
    last_name: str
    password: str = Field(None, min_length=4)
