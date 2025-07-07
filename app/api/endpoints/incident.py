from fastapi import APIRouter
from app.models.requests import (IncidentRequest)
from app.models.response import ClassificationWithStaffResponse
from app.services.classification import AIClassificationService
from app.utils.logging import logger
from datetime import datetime

router=APIRouter()

classification_service = AIClassificationService()
@router.post("/classify-summarize", response_model=ClassificationWithStaffResponse)
async def classify_incident_only(
    incident: IncidentRequest,
):
    return await classification_service.classify_incident(incident)
