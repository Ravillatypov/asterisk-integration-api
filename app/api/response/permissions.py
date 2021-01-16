from typing import List

from pydantic import BaseModel, Field


class ResponsePermission(BaseModel):
    id: int = Field(alias='value')
    name: str

    class Config:
        orm_mode = True


class ResponsePermissions(BaseModel):
    result: List[ResponsePermission]
