from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, validator

from app.config import app_config
from app.consts import CallType, CallState
from .tag import ResponseTag
from ...models import Call


class ResponseCall(BaseModel):
    id: str
    started_at: datetime
    voice_started_at: datetime = None
    finished_at: datetime = None
    call_type: str = Field(enum=CallType.all())
    state: str = Field(enum=CallState.all())
    is_record: bool
    from_pin: str
    from_number: str
    request_pin: str
    request_number: str
    account_id: str = None
    waiting_time: str = None
    duration: int = None
    comment: str = None
    tags: List[ResponseTag] = []

    class Config:
        orm_mode = True

    @validator('tags', pre=True)
    def _tags(cls, val):
        if isinstance(val, list):
            return val

        return [ResponseTag.from_orm(i) for i in val.related_objects]

    @validator('request_pin', pre=True)
    def _request_pin(cls, val: str):
        if val in app_config.ats.group_numbers:
            return ''

        return val


class ResponseCallsList(BaseModel):
    result: List[ResponseCall]
    count: int

    def __init__(self, calls: List[Call]):
        super().__init__(
            result=[ResponseCall.from_orm(call) for call in calls],
            count=len(calls),
        )
