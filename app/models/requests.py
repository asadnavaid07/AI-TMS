from pydantic import BaseModel,Field
from typing import Optional

class IncidentRequest(BaseModel):
    description:str = Field(...,min_length=10,max_length=2000)



class RegenerateRequest(BaseModel):
    summary:str
    email:str
