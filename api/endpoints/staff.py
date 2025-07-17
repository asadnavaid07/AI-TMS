from fastapi import HTTPException, APIRouter
from typing import List, Any, Dict

import httpx
from models.staff_validations import StaffRecord

router = APIRouter()

stored_staff_data: List[StaffRecord] = []

@router.get("/api/staff", response_model=Dict[str, Any])
async def get_staff_data():
    try:
        # Power Automate HTTP trigger URL
        power_automate_url = (
            "https://5f257beee4e8e7459c386335509b51.00.environment.api.powerplatform.com:443"
            "/powerautomate/automations/direct/workflows/3a1112fadb5b43d68c8a52b8f26efc01"
            "/triggers/manual/paths/invoke/?api-version=1&tenantId=tId"
            "&environmentName=5f257bee-e4e8-e745-9c38-6335509b5100"
            "&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=efZ9TBpZp1te-ko_d4CaPIS2fhLfb8BGbLguWNdoJg4"
        )

        async with httpx.AsyncClient() as client:
            # Make GET request to Power Automate trigger
            response = await client.get(power_automate_url)

            # Check if the request was successful
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Power Automate API request failed: {response.text}"
                )

            # Parse the response data
            response_data = response.json()

            # Check if response is a list; if not, check for 'value' key
            if isinstance(response_data, list):
                staff_records = response_data
            else:
                staff_records = response_data.get("value", response_data)

            # Ensure staff_records is a list
            if not isinstance(staff_records, list):
                raise HTTPException(
                    status_code=400,
                    detail="Unexpected response format from Power Automate API"
                )

            # Validate and convert response data to StaffRecord models
            try:
                global stored_staff_data
                stored_staff_data = [StaffRecord(**record) for record in staff_records]
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error parsing staff data: {str(e)}"
                )

        if not stored_staff_data:
            raise HTTPException(status_code=404, detail="No staff data retrieved")

        return {
            "message": "Staff data retrieved successfully",
            "records_retrieved": len(stored_staff_data),
            "status": "success",
            "data": [record.model_dump(by_alias=True) for record in stored_staff_data]
        }

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Power Automate API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving staff data: {str(e)}")
    
