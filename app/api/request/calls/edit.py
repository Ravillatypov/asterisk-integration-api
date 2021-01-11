from typing import List

from pydantic import BaseModel


class RequestCallEdit(BaseModel):
    id: str
    comment: str = None
    tags: List[str] = None
