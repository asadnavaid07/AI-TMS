from pydantic import BaseModel,Field
from typing import Optional

class IncidentRequest(BaseModel):
    description:str = Field(...,min_length=10,max_length=2000)


class StaffRequest(BaseModel):
    department: Optional[str] = None
    availability: Optional[bool] = None
    skillset: Optional[str] = None

