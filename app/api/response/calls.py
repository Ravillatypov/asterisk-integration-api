from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.consts import CallType, CallState


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
    tags: List[int] = None

    class Config:
        orm_mode = True


class ResponseCallsList(BaseModel):
    result: List[ResponseCall]
