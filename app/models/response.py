from pydantic import BaseModel
from typing import List,Dict
from typing import Optional

class AIClassificationResponse(BaseModel):
    category: str
    severity: str
    summary: str
    email:str

class StaffAssignment(BaseModel):
    assigned_staff_email: Optional[str] = None
    assigned_staff_name: Optional[str] = None
    assigned_department: str
    staff_skillset: Optional[str] = None

class ClassificationWithStaffResponse(BaseModel):
    classification: AIClassificationResponse
    staff_assignment: StaffAssignment


class RegenerateResponse(BaseModel):
    summary: str
    email:str