from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from app.consts import CallState, CallType


def _get_last_week():
    now = datetime.utcnow()
    return now - timedelta(weeks=1)


class RequestGetCalls(BaseModel):
    state: CallState = Field(None, parameter='query')
    need_recall: bool = Field(None, parameter='query')
    started_from: datetime = Field(default_factory=_get_last_week, parameter='query')
    started_to: datetime = Field(None, parameter='query')
    call_type: CallType = Field(None, parameter='query')
    limit: int = Field(1000, parameter='query')
    offset: int = Field(0, parameter='query')
