from services.staff_data import get_staff_data
from utils.types import SkillIndex
from typing import Set

class SkillIndexer:
    def __init__(self):
        self.skill_index = self.build_skill_index()

    def build_skill_index(self) -> SkillIndex:

        index: SkillIndex = {}
        for staff in get_staff_data():
            if staff.get("cr6dd_availability", False):
                skills = [skill.strip().lower() for skill in staff["cr6dd_skillset"].split(",")]
                for skill in skills:
                    if skill not in index:
                        index[skill] = []
                    index[skill].append({
                        "department": staff["cr6dd_departmentname"],
                        "name": staff["cr6dd_UserID"]["cr6dd_name"],
                        "email": staff["cr6dd_UserID"]["cr6dd_email"],
                        "staffid": staff["cr6dd_staff1id"],
                        "skillset": staff["cr6dd_skillset"]
                    })
        return index

    def get_available_departments(self) -> Set[str]:
        """Returns a set of available departments with available staff."""
        return {staff["cr6dd_departmentname"] for staff in get_staff_data() if staff.get("cr6dd_availability", False)}