from typing import Optional, List

from pydantic import BaseModel

from app.models import Tag


class ResponseTag(BaseModel):
    id: int
    name: str
    color: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True


class ResponseTags(BaseModel):
    result: List[ResponseTag]

    def __init__(self, tags: List[Tag]):
        super().__init__(result=[ResponseTag.from_orm(i) for i in tags])
