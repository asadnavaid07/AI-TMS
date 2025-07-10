import json
from datetime import datetime
from fastapi import HTTPException
from typing import Dict, Any, List, Optional, Tuple
from app.models.requests import IncidentRequest
from app.services.ai_service import AzureClient
from app.utils.logging import logger
from app.services.sample_data import SAMPLE_STAFF_DATA


class AIClassificationService:
    def __init__(self):
        self.ai_client = AzureClient()
        self.combined_prompt = """
        You are an expert IT incident analyst and staff assignment specialist. Analyze the following incident and provide a structured classification, department mapping, and staff assignment based on available staff data.
        You must analyze the incident in ANY language but respond ONLY in English using the specified JSON format.
        Incident Description: "{description}"

        Available Staff Data:
        {staff_data}

        Instructions:
        1. Classify the incident based on its description, considering:
           - Business impact and urgency
           - Technical complexity
           - Security implications
           - Resource requirements
        2. Map the incident to the most appropriate department based on the staff's skillsets and availability.
        3. Select the best available staff member (with staff ID and staff code) from the chosen department by semantically matching the incident description to their skillset.
        4. If no suitable department or staff is found, default to the "Admin" department and select an available staff member from Admin.
        5. Only consider staff with "availability": true.
        6. Fallback for Controversial or Problematic Descriptions:
           - If the incident description is ambiguous, controversial, offensive, or cannot be clearly classified (e.g., contains inappropriate language, lacks sufficient detail, or raises ethical concerns), classify it as:
             - category: "Unclassified"
             - severity: "Low"
             - summary: "Incident could not be classified due to ambiguous or problematic description."
             And assign to an available Admin staff member.
        Respond with ONLY a valid JSON object containing:
        {{
            "category": "brief category description (e.g., 'Network Issue', 'Security Problem', 'HR Query', etc.)",
            "severity": "one of: Low, Medium, High",
            "summary": "concise 1-2 sentence summary",
            "email": "professional email body for assigned staff",
            "best_department": "exact department name from staff data (e.g., 'IT', 'HR', 'Finance', 'Admin')",
            "department_reasoning": "brief explanation of why this department was chosen",
            "department_confidence_score": <integer between 0-100>,
            "assigned_staff_email": "staff Email (cr6dd_email) of the selected staff",
            "assigned_staff_name": "staff name (cr6dd_name) of the selected staff",
            "staff_skillset": "skillset of the selected staff",
            "staff_assignment_status": "one of: 'assigned', 'assigned_fallback', 'no_staff_available'",
            "skillset_match_score": <integer between 0-100 or 0 if no staff assigned>,
            "staff_match_reasoning": "brief explanation of why this staff was chosen or why none was assigned"
        }}

        Respond ONLY with the JSON object, no additional text or formatting.
        """

    def get_staff_data(self):
        try:
            from app.api.endpoints.staff import stored_staff_data
            return stored_staff_data if stored_staff_data else SAMPLE_STAFF_DATA
        except (ImportError, AttributeError):
            return SAMPLE_STAFF_DATA

    def format_staff_data_for_prompt(self):
        staff_data = self.get_staff_data()
        formatted = []
        for staff in staff_data:
            formatted.append(
                f"Department: {staff.get('cr6dd_department@OData.Community.Display.V1.FormattedValue', '')}, "
                f"Skillset: {staff.get('cr6dd_skillset', '')}, "
                f"Staff Email: {staff.get('cr6dd_email', '')}, "
                f"Staff Name: {staff.get('cr6dd_name', '')}, "
                f"Availability: {'Yes' if staff.get('cr6dd_availability', False) else 'No'}"
            )
        return "\n".join(formatted)

    def select_admin_staff(self, staff_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select an available staff member from the Admin department."""
        admin_staff = [
            staff for staff in staff_data 
            if staff.get("cr6dd_department@OData.Community.Display.V1.FormattedValue") == "Admin" 
            and staff.get("cr6dd_availability", False)
        ]
        return admin_staff[0] if admin_staff else None

    async def classify_incident(self, incident: IncidentRequest) -> Dict[str, Any]:
        try:
            start_time = datetime.now()
            staff_data = self.get_staff_data()

            prompt = self.combined_prompt.format(
                description=incident.description,
                staff_data=self.format_staff_data_for_prompt()
            )

            messages = [
                {"role": "system", "content": "You are an expert IT incident classifier and staff assignment specialist. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = await self.ai_client.create_chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )

            ai_response = response['choices'][0]["message"]["content"].strip()

            # Clean up AI response to extract valid JSON
            if ai_response.startswith("```json"):
                ai_response = ai_response[7:-3]
            elif ai_response.startswith("```"):
                ai_response = ai_response[3:-3]
            
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                ai_response = ai_response[json_start:json_end]
            
            response_data = json.loads(ai_response)

            departments = {staff["cr6dd_department@OData.Community.Display.V1.FormattedValue"] for staff in staff_data}
            best_department = response_data.get("best_department", "Admin")
            if best_department not in departments:
                logger.warning(f"AI suggested department '{best_department}' not found in staff data. Defaulting to Admin.")
                admin_staff = self.select_admin_staff(staff_data)
                response_data["best_department"] = "Admin"
                response_data["department_reasoning"] = f"Fallback to Admin: Invalid department '{best_department}' not found in staff data."
                response_data["department_confidence_score"] = 0
                if admin_staff:
                    response_data["assigned_staff_email"] = admin_staff["cr6dd_email"]
                    response_data["assigned_staff_name"] = admin_staff["cr6dd_name"]
                    response_data["staff_skillset"] = admin_staff["cr6dd_skillset"]
                    response_data["staff_assignment_status"] = "assigned_fallback"
                    response_data["skillset_match_score"] = 50
                    response_data["staff_match_reasoning"] = "Assigned to available Admin staff due to invalid department."
                else:
                    response_data["assigned_staff_email"] = None
                    response_data["assigned_staff_name"] = None
                    response_data["staff_skillset"] = None
                    response_data["staff_assignment_status"] = "no_staff_available"
                    response_data["skillset_match_score"] = 0
                    response_data["staff_match_reasoning"] = "No available staff in Admin department."

            # Validate assigned staff
            if response_data.get("assigned_staff_email"):
                staff = next((s for s in staff_data if s["cr6dd_email"] == response_data["assigned_staff_email"]), None)
                if staff and staff["cr6dd_availability"]:
                    if staff["cr6dd_department@OData.Community.Display.V1.FormattedValue"] != response_data["best_department"]:
                        logger.warning(f"Assigned staff {response_data['assigned_staff_email']} does not belong to {response_data['best_department']}. Defaulting to Admin staff.")
                        admin_staff = self.select_admin_staff(staff_data)
                        response_data["best_department"] = "Admin"
                        response_data["department_reasoning"] = f"Fallback to Admin: Assigned staff does not match department {response_data['best_department']}."
                        response_data["department_confidence_score"] = 0
                        if admin_staff:
                            response_data["assigned_staff_email"] = admin_staff["cr6dd_email"]
                            response_data["assigned_staff_name"] = admin_staff["cr6dd_name"]
                            response_data["staff_skillset"] = admin_staff["cr6dd_skillset"]
                            response_data["staff_assignment_status"] = "assigned_fallback"
                            response_data["skillset_match_score"] = 50
                            response_data["staff_match_reasoning"] = "Assigned to available Admin staff due to department mismatch."

                elif not staff or not staff["cr6dd_availability"]:
                    logger.warning(f"Assigned staff {response_data['assigned_staff_email']} is invalid or unavailable. Defaulting to Admin staff.")
                    admin_staff = self.select_admin_staff(staff_data)
                    response_data["best_department"] = "Admin"
                    response_data["department_reasoning"] = f"Fallback to Admin: Assigned staff is unavailable or invalid."
                    response_data["department_confidence_score"] = 0
                    if admin_staff:
                        response_data["assigned_staff_email"] = admin_staff["cr6dd_email"]
                        response_data["assigned_staff_name"] = admin_staff["cr6dd_name"]
                        response_data["staff_skillset"] = admin_staff["cr6dd_skillset"]
                        response_data["staff_assignment_status"] = "assigned_fallback"
                        response_data["skillset_match_score"] = 50
                        response_data["staff_match_reasoning"] = "Assigned to available Admin staff due to unavailable or invalid staff."
                    else:
                        response_data["assigned_staff_email"] = None
                        response_data["assigned_staff_name"] = None
                        response_data["staff_skillset"] = None
                        response_data["staff_assignment_status"] = "no_staff_available"
                        response_data["skillset_match_score"] = 0
                        response_data["staff_match_reasoning"] = "No available staff in Admin department."

            if response_data.get("category") == "Unclassified":
                logger.warning(f"AI response indicates unclassified or problematic incident: {response_data}")
                admin_staff = self.select_admin_staff(staff_data)
                response_data["best_department"] = "Admin"
                response_data["department_reasoning"] = "Defaulted to Admin due to unclassified or problematic incident description."
                response_data["department_confidence_score"] = 0
                if admin_staff:
                    response_data["assigned_staff_email"] = admin_staff["cr6dd_email"]
                    response_data["assigned_staff_name"] = admin_staff["cr6dd_name"]
                    response_data["staff_skillset"] = admin_staff["cr6dd_skillset"]
                    response_data["staff_assignment_status"] = "assigned_fallback"
                    response_data["skillset_match_score"] = 50
                    response_data["staff_match_reasoning"] = "Assigned to available Admin staff due to unclassified or problematic incident description."
            classification_response = {
                "category": response_data.get("category", "General"),
                "severity": response_data.get("severity", "Medium"),
                "summary": response_data.get("summary", "Incident classification summary"),
                "email": response_data.get("email", "Incident classification email")
            }

            staff_assignment = {
                "assigned_staff_email": response_data.get("assigned_staff_email"),
                "assigned_staff_name": response_data.get("assigned_staff_name"),
                "assigned_department": response_data.get("best_department"),
                "staff_skillset": response_data.get("staff_skillset"),
            }

            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.info(f"Classification completed in {processing_time:.2f}ms")

            return {
                "classification": classification_response,
                "staff_assignment": staff_assignment,
                "processing_time_ms": processing_time,
                "timestamp": datetime.now()
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw AI response: {ai_response}")
            raise HTTPException(status_code=500, detail="AI response parsing failed")
        except Exception as e:
            logger.error(f"Classification error: {e}")
            raise HTTPException(status_code=500, detail="Classification service error")