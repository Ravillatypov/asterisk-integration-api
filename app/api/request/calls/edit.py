from typing import List

from pydantic import BaseModel
from ..tag import RequestTag


class RequestCallEdit(BaseModel):
    id: str
    comment: str = None
    tags: List[RequestTag] = None
