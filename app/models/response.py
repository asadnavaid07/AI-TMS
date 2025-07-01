from pydantic import BaseModel,Field
from typing import List
from datetime import datetime
from .enums import CategoryEnum,SeverityEnum
from typing import Optional

class AIClassificationResponse(BaseModel):
    category:CategoryEnum
    severity:SeverityEnum
    confidence_score:float = Field(...,ge=0.0,le=1.0)
    summary:str
    estimated_resolution_time:str
    assigned_time:str
    priority_score: int = Field(..., ge=1, le=10)
    assigned_time: Optional[datetime] = None 


class AIResponseSuggestion(BaseModel):
    suggested_response: str
    escalation_needed: bool
    next_actions: List[str]
    knowledge_base_articles: List[str]

class IncidentAnalysis(BaseModel):
    classfication:AIClassificationResponse
    response_suggestion:AIResponseSuggestion
    processing_time_ms:int
    timestamp:datetime

class CategoriesResponse(BaseModel):
    categories: List[str]

class SeveritiesResponse(BaseModel):
    severities: List[str]