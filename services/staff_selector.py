from typing import List, Optional
from .staff_data import get_staff_data
from utils.types import Staff
from config import DEFAULT_FALLBACK_DEPARTMENT
from utils.logging import logger

class StaffSelector:
    def select_best_staff(self, required_skills: List[str], department: str) -> Optional[Staff]:
        """Selects the best staff member based on skill matching and availability."""
        staff_data = get_staff_data()
        if not staff_data:
            logger.error(f"No staff data available for department: {department}")
            return None

        best_staff = None
        best_score = 0

        # First attempt: prioritize skill matching
        for staff in staff_data:
            if staff["cr6dd_departmentname"] == department and staff.get("cr6dd_availability", False):
                staff_skills = set(skill.strip().lower() for skill in staff["cr6dd_skillset"].split(","))
                required_skills_set = set(skill.lower() for skill in required_skills)
                match_score = len(staff_skills.intersection(required_skills_set))
                # logger.debug(f"Evaluating staff {staff["cr6dd_UserID"]['cr6dd_name']} in {department}: match_score={match_score}, skills={staff_skills}")
                if match_score > best_score:
                    best_score = match_score
                    best_staff = staff

        # For Admin fallback, select any available staff if no skill match found
        if not best_staff and department == DEFAULT_FALLBACK_DEPARTMENT:
            for staff in staff_data:
                if staff["cr6dd_departmentname"] == department and staff.get("cr6dd_availability", False):
                    best_staff = staff
                    logger.info(f"No skill match for Admin fallback, selecting available staff: {staff["cr6dd_UserID"]['cr6dd_name']}")
                    break

        if not best_staff:
            logger.warning(f"No available staff found for department: {department} with skills: {required_skills}")
        else:
            logger.info(f"Selected staff {best_staff["cr6dd_UserID"]['cr6dd_name']} for department: {department}")

        return best_staff