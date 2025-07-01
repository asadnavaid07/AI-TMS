from fastapi import APIRouter, BackgroundTasks, Depends
from app.models import (
    IncidentRequest, 
    IncidentAnalysis, 
    AIClassificationResponse, 
    AIResponseSuggestion,
    CategoriesResponse,
    SeveritiesResponse,
    CategoryEnum,
    SeverityEnum
)
from app.services.classification import AIClassificationService
from app.utils.background import log_incident_metrics
from app.utils.logging import logger
from datetime import datetime

router=APIRouter()

classification_service = AIClassificationService()
# response_service = ResponseSuggestionService()

# @router.post("/analyze-incident", response_model=IncidentAnalysis)
# async def analyze_incident(
#     incident: IncidentRequest,
#     background_tasks: BackgroundTasks,
# ):
#     """Main endpoint for incident analysis - called by Power Automate"""
#     start_time = datetime.now()
    
#     try:
#         logger.info(f"Processing incident: {incident.title}")
        
#         # Step 1: Classify the incident
#         classification = await classification_service.classify_incident(incident)
        
#         # Step 2: Generate response suggestion
#         response_suggestion = await response_service.generate_response(incident, classification)
        
#         # Calculate processing time
#         processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
#         # Create analysis result
#         analysis = IncidentAnalysis(
#             classification=classification,
#             response_suggestion=response_suggestion,
#             processing_time_ms=processing_time,
#             timestamp=datetime.now()
#         )
        
#         # Add background task for logging/metrics
#         background_tasks.add_task(log_incident_metrics, incident, analysis)
        
#         return analysis
        
#     except Exception as e:
#         logger.error(f"Analysis failed: {e}")
#         raise

@router.post("/classify-only", response_model=AIClassificationResponse)
async def classify_incident_only(
    incident: IncidentRequest,
):
    """Endpoint for classification only"""
    return await classification_service.classify_incident(incident)

# @router.post("/suggest-response", response_model=AIResponseSuggestion)
# async def suggest_response_only(
#     incident: IncidentRequest,
#     classification: AIClassificationResponse,
# ):
#     """Endpoint for response suggestion only"""
#     return await response_service.generate_response(incident, classification)

# @router.get("/categories", response_model=CategoriesResponse)
# async def get_categories():
#     return CategoriesResponse(categories=[category.value for category in CategoryEnum])

# @router.get("/severities", response_model=SeveritiesResponse)
# async def get_severities():
#     return SeveritiesResponse(severities=[severity.value for severity in SeverityEnum])