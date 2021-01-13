from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from app.consts import CallState, CallType


class RequestGetCalls(BaseModel):
    state: CallState = Field(None, parameter='query')
    need_recall: bool = Field(None, parameter='query')
    started_from: datetime = Field(default_factory=lambda _: datetime.utcnow() - timedelta(days=30), parameter='query')
    started_to: datetime = Field(None, parameter='query')
    call_type: CallType = Field(None, parameter='query')
    limit: int = Field(10000, parameter='query')
    offset: int = Field(0, parameter='query')
