from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class MemberCreate(BaseModel):
    name: str
    national_id: str
    date_joined: date  

class MemberResponse(BaseModel):
    id: Optional[int]
    name: str
    national_id: str
    date_joined: date  

    model_config = ConfigDict(from_attributes=True)