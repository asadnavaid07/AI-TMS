from fastapi import APIRouter
from app.api.endpoints.incident import router as incident_router
# from app.api.endpoints.staff import router as get_staff_router

api_router = APIRouter()


api_router.include_router(
    incident_router, 
    prefix="/incidents",  
    tags=["incidents"]
)

# api_router.include_router(
#     get_staff_router, 
#     prefix="/get-staff",  
#     tags=["get-staff"]
# )
