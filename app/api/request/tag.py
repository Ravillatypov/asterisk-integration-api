from pydantic import BaseModel


class RequestTag(BaseModel):
    name: str
    color: str = None
    description: str = None
