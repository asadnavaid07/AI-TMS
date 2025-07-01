
from fastapi import APIRouter
from app.api.endpoints.incident import router as incident_router


api_router = APIRouter()


api_router.include_router(
    incident_router, 
    prefix="/incidents",  
    tags=["incidents"]
)
