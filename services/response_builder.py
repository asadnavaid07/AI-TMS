from typing import Dict, Any, Optional, List
from .staff_selector import StaffSelector
from config import DEFAULT_FALLBACK_DEPARTMENT, DEFAULT_FALLBACK_SKILLS
from utils.types import ClassificationResponse, Staff
from utils.logging import logger

class ResponseBuilder:
    def __init__(self, staff_selector: StaffSelector):
        self.staff_selector = staff_selector

    def create_fallback_response(self, reason: str, is_unclassified: bool = False) -> ClassificationResponse:
        admin_staff = self.staff_selector.select_best_staff(DEFAULT_FALLBACK_SKILLS, DEFAULT_FALLBACK_DEPARTMENT)
        category = "Unclassified" if is_unclassified else "Manual Assignment Required"
        summary = f"Incident flagged for review: {reason}"

        if is_unclassified and not admin_staff:
            logger.error(f"No available Admin staff for Unclassified fallback response. Reason: {reason}")
            return {
                "classification": {
                    "category": category,
                    "severity": "Low",
                    "department": DEFAULT_FALLBACK_DEPARTMENT,
                    "required_skills": DEFAULT_FALLBACK_SKILLS,
                    "title": "Undefined",
                    "summary": summary,
                    "email": "This incident requires manual review due to no available staff. Please assign to an appropriate team."
                },
                "staff_assignment": {
                    "assigned_staff_email": None,
                    "assigned_staff_name": None,
                    "assigned_staff_id": None,
                    "assigned_department": DEFAULT_FALLBACK_DEPARTMENT,
                    "staff_skillset": None,
                    "assignment_status": "no_staff_available",
                    "assignment_reason": f"No available staff in {DEFAULT_FALLBACK_DEPARTMENT} department."
                },
                "processing_details": {
                    "fallback_reason": reason,
                    "department_available": False
                }
            }

        if not admin_staff:
            logger.error(f"No available Admin staff for {category} fallback response. Reason: {reason}")
            raise ValueError(f"Cannot create fallback response: No available staff in {DEFAULT_FALLBACK_DEPARTMENT} for {category} case")

        # logger.info(f"Creating fallback response for Admin staff: {admin_staff["cr6dd_UserID"]['cr6dd_name']}")
        return {
            "classification": {
                "category": category,
                "severity": "Low",
                "department": DEFAULT_FALLBACK_DEPARTMENT,
                "required_skills": DEFAULT_FALLBACK_SKILLS,
                "title": "Undefined",
                "summary": summary,
                "email": f"Dear Admin, this incident requires manual review due to: {reason}. Please assign to the appropriate team or handle accordingly."
                # "email": f"Dear {admin_staff["cr6dd_UserID"]['cr6dd_name']}, this incident requires manual review due to: {reason}. Please assign to the appropriate team or handle accordingly."
            },
            "staff_assignment": {
                "assigned_staff_email": admin_staff["cr6dd_UserID"]["cr6dd_email"],
                "assigned_staff_name": admin_staff["cr6dd_UserID"]["cr6dd_name"],
                "assigned_staff_id": admin_staff["cr6dd_staff1id"],
                "assigned_department": DEFAULT_FALLBACK_DEPARTMENT,
                "staff_skillset": admin_staff["cr6dd_skillset"],
                "assignment_status": "assigned_fallback",
                "assignment_reason": f"Assigned to {DEFAULT_FALLBACK_DEPARTMENT} due to: {reason}"
            },
            "processing_details": {
                "fallback_reason": reason,
                "department_available": True
            }
        }

    def create_classification_response(
        self,
        classification_data: Dict[str, Any],
        assigned_staff: Staff,
        target_department: str,
        required_skills: List[str],
        original_department: str
    ) -> ClassificationResponse:
        """Creates a response for a successfully classified incident."""
        return {
            "classification": {
                "category": classification_data.get("category", "Manual Assignment Required"),
                "severity": classification_data.get("severity", "Medium"),
                "department": target_department,
                "required_skills": required_skills,
                "title": classification_data.get("title", "Incident classification title"),
                "summary": classification_data.get("summary", "Incident classification summary"),
                "email": classification_data.get("email", f"Incident assigned to {target_department} for review")
            },
            "staff_assignment": {
                "assigned_staff_email": assigned_staff["cr6dd_UserID"]["cr6dd_email"],
                "assigned_staff_name": assigned_staff["cr6dd_UserID"]["cr6dd_name"],
                "assigned_staff_id": assigned_staff["cr6dd_staff1id"],
                "assigned_department": target_department,
                "staff_skillset": assigned_staff["cr6dd_skillset"],
                "assignment_status": "assigned",
                "assignment_reason": f"Matched to {target_department} based on required skills: {', '.join(required_skills)}"
            },
            "processing_details": {
                "department_match": target_department == original_department,
                "fallback_used": target_department != original_department
            }
        }