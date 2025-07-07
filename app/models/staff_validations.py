from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict



class StaffRecord(BaseModel):
    odata_type: str = Field(alias="@odata.type")
    odata_id: str = Field(alias="@odata.id")
    odata_etag: str = Field(alias="@odata.etag")
    odata_editLink: str = Field(alias="@odata.editLink")
    department_formatted: str = Field(alias="cr6dd_department@OData.Community.Display.V1.FormattedValue")
    department: int = Field(alias="cr6dd_department")
    skillset: str = Field(alias="cr6dd_skillset")
    staffid_type: str = Field(alias="cr6dd_staffid@odata.type")
    staffid: str = Field(alias="cr6dd_staffid")
    newcolumn: str = Field(alias="cr6dd_newcolumn")
    availability_formatted: str = Field(alias="cr6dd_availability@OData.Community.Display.V1.FormattedValue")
    availability: bool = Field(alias="cr6dd_availability")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "@odata.type": "#Microsoft.Dynamics.CRM.cr6dd_staff",
                "@odata.id": "https://org2d697781.crm.dynamics.com/api/data/v9.1/cr6dd_staffs(ace478dc-6057-f011-bec2-000d3a5c4fb0)",
                "@odata.etag": "W/\"2637546\"",
                "@odata.editLink": "cr6dd_staffs(ace478dc-6057-f011-bec2-000d3a5c4fb0)",
                "cr6dd_department@OData.Community.Display.V1.FormattedValue": "IT",
                "cr6dd_department": 594700000,
                "cr6dd_skillset": "I can handle security problems",
                "cr6dd_staffid@odata.type": "#Guid",
                "cr6dd_staffid": "ace478dc-6057-f011-bec2-000d3a5c4fb0",
                "cr6dd_newcolumn": "001",
                "cr6dd_availability@OData.Community.Display.V1.FormattedValue": "Yes",
                "cr6dd_availability": True
            }
        }

class StaffDataRequest(BaseModel):
    staff_data: List[Dict[str, Any]]

class StaffFilterRequest(BaseModel):
    department: Optional[str] = None
    availability: Optional[bool] = None
    skillset: Optional[str] = None
