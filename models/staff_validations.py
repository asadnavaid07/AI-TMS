from fastapi import HTTPException, APIRouter
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from typing import Optional


class UserRecord(BaseModel):
    odata_type: str = Field(alias="@odata.type")
    odata_id: str = Field(alias="@odata.id")
    odata_editLink: str = Field(alias="@odata.editLink")
    name: str = Field(alias="cr6dd_name")
    email: str = Field(alias="cr6dd_email")
    usersid_type: str = Field(alias="cr6dd_usersid@odata.type")
    usersid: str = Field(alias="cr6dd_usersid")

    class Config:
        allow_population_by_field_name = True

class StaffRecord(BaseModel):
    odata_type: str = Field(alias="@odata.type")
    odata_id: str = Field(alias="@odata.id")
    odata_etag: str = Field(alias="@odata.etag")
    odata_editLink: str = Field(alias="@odata.editLink")
    staffid: str = Field(alias="cr6dd_staffid")
    skillset: str = Field(alias="cr6dd_skillset")
    departmentname: str= Field(alias="cr6dd_departmentname")  
    staff1id_type: str = Field(alias="cr6dd_staff1id@odata.type")
    staff1id: str = Field(alias="cr6dd_staff1id")
    availability: bool = Field(alias="cr6dd_availability")
    user_id_association_link: str = Field(alias="cr6dd_UserID@odata.associationLink")
    user_id_navigation_link: str = Field(alias="cr6dd_UserID@odata.navigationLink")
    user_id: Optional[UserRecord] = Field(alias="cr6dd_UserID")

    class Config:
        allow_population_by_field_name = True

class StaffDataRequest(BaseModel):
    staff_data: List[StaffRecord]
