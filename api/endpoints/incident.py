from fastapi import APIRouter
from models.requests import (IncidentRequest)
from models.requests import (RegenerateRequest)
from models.response import ClassificationWithStaffResponse,RegenerateResponse
from services.classification import AIClassificationService
from services.regenerate import AIRegenerator
from utils.logging import logger
from datetime import datetime

router=APIRouter()

classification_service = AIClassificationService()
regenerator=AIRegenerator()

@router.post("/classify-summarize", response_model=ClassificationWithStaffResponse)
async def classify_incident_only(
    incident: IncidentRequest,
):
    return await classification_service.classify_incident(incident)


@router.post("/regenerate",response_model=RegenerateResponse)
async def regenerate_response(
    regenerate:RegenerateRequest
):
    return await regenerator.regenerate(regenerate)
