from pydantic import BaseModel


class RequestCallback(BaseModel):
    from_pin: str
    request_number: str
