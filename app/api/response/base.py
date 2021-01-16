from typing import List

from pydantic import BaseModel


class ResponseSuccess(BaseModel):
    success: bool = True


class ErrorSchema(BaseModel):
    message: str
    code: int = None


class ResponseError(BaseModel):
    success: bool = False
    errors: List[ErrorSchema]
