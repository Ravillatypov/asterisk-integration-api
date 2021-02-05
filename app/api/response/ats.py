from typing import List

from pydantic import BaseModel


class ResponseAtsInfo(BaseModel):
    company_name: str
    company_logo: str
    external_numbers: List[str]
    group_numbers: List[str]
