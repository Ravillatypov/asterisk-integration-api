from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from app.consts import CallState, CallType


class RequestGetCalls(BaseModel):
    state: Optional[CallState]
    need_recall: Optional[bool]
    started_from: Optional[datetime] = Field(default_factory=lambda _: datetime.utcnow() - timedelta(days=30))
    started_to: Optional[datetime]
    call_type: Optional[CallType]
    limit: Optional[int] = 100
    offset: Optional[int] = 0
