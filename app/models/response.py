from pydantic import BaseModel
from typing import List
from typing import Optional

class AIClassificationResponse(BaseModel):
    category: str
    severity: str
    summary: str

class StaffAssignment(BaseModel):
    assigned_staff_id: Optional[str] = None
    assigned_staff_code: Optional[str] = None
    assigned_department: str
    staff_skillset: Optional[str] = None

class ClassificationWithStaffResponse(BaseModel):
    classification: AIClassificationResponse
    staff_assignment: StaffAssignment


class IncidentRequest(BaseModel):
    description: str
    priority: Optional[str] = None
    requester: Optional[str] = None



class CategoriesResponse(BaseModel):
    categories: List[str]

class SeveritiesResponse(BaseModel):
    severities: List[str]
