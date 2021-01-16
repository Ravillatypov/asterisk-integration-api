from pydantic import BaseModel, validator


class RequestTag(BaseModel):
    name: str
    color: str = None
    description: str = None

    @validator('name', pre=True)
    def _name(cls, val: str):
        return val.strip().title()
