from pydantic import BaseModel,Field
from typing import Optional

class IncidentRequest(BaseModel):
    title:str = Field(...,min_length=5,max_length=200)
    description:str = Field(...,min_length=10,max_length=2000)
    reporter_email:str = Field(...,)
    reporter_name:str = Field(...,min_length=2,max_length=100)
    department: Optional[str] = None
    urgency_level: Optional[str] = None

# regex=r'^[\w\.-]+@[\w\.-]+\.\w+$'
