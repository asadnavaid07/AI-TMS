from fastapi import HTTPException, APIRouter
from typing import List, Any, Dict


router = APIRouter()


stored_staff_data = []

@router.post("/api/staff/receive", response_model=Dict[str, Any])
async def receive_staff_data(staff_data: List[Dict[str, Any]]):
    try:
        if not staff_data:
            raise HTTPException(status_code=400, detail="No staff data provided")
        
        global stored_staff_data
        stored_staff_data = staff_data
        print(staff_data)
        
        return {
            "message": "Staff data received successfully",
            "records_received": len(staff_data),
            "status": "success",
            "data": staff_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing staff data: {str(e)}")

