import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from models.requests import IncidentRequest
from services.ai_service import AzureClient
from utils.logging import logger
from services.sample_data import SAMPLE_STAFF_DATA


class AIClassificationService:
    def __init__(self):
        self.ai_client = AzureClient()
        self.inappropriate_patterns = [
            r'\b(fuck|shit|damn|bitch|asshole|crap)\b',
            r'\b(hate|kill|die|murder|suicide)\b',
            r'\b(porn|sex|nude|naked)\b',
            r'\b(racist|sexist|homophobic)\b'
        ]
        self.category_department_mapping = {
            "Network Issue": "IT",
            "Hardware Problem": "IT", 
            "Software Issue": "IT",
            "Security Problem": "IT",
            "Email Issue": "IT",
            "System Error": "IT",
            "Database Issue": "IT",
            "Server Issue": "IT",
            "Password Reset": "IT",
            "Account Issue": "IT",
            
            "HR Query": "HR",
            "Employee Issue": "HR",
            "Leave Request": "HR",
            "Payroll Issue": "HR",
            "Benefits Question": "HR",
            "Training Request": "HR",
            
            "Financial Query": "Finance",
            "Budget Issue": "Finance",
            "Invoice Problem": "Finance",
            "Expense Report": "Finance",
            "Payment Issue": "Finance",
            
            "General Query": "Admin",
            "Facility Issue": "Admin",
            "Office Supply": "Admin",
            "Maintenance Request": "Admin",
            "Unclassified": "Admin"
        }


    def get_staff_data(self) -> List[Dict[str, Any]]:
        return SAMPLE_STAFF_DATA

    def get_available_departments(self) -> Set[str]:
        staff_data = self.get_staff_data()
        available_departments = set()
        print(available_departments)
        
        for staff in staff_data:
            if staff.get("cr6dd_availability", False):
                dept = staff.get("cr6dd_department@OData.Community.Display.V1.FormattedValue", "")
                if dept:
                    available_departments.add(dept)
        
        return available_departments



    def is_inappropriate_content(self, description: str) -> bool:
        description_lower = description.lower()
        
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, description_lower, re.IGNORECASE):
                return True
        
        return False


    def is_ambiguous_description(self, description: str) -> bool:
        description = description.strip()
        
        if len(description) < 10:
            return True
            
        if len(set(description.lower().replace(' ', ''))) < 3:
            return True
            
        if re.match(r'^[0-9\s\W]+$', description):
            return True
            
        return False


    def select_staff_from_department(self, department: str) -> Optional[Dict[str, Any]]:
        """Select an available staff member from the specified department."""
        staff_data = self.get_staff_data()
        
        department_staff = [
            staff for staff in staff_data 
            if staff.get("cr6dd_department@OData.Community.Display.V1.FormattedValue") == department
            and staff.get("cr6dd_availability", False)
        ]
        
        return department_staff[0] if department_staff else None



    def create_classification_prompt(self, description: str) -> str:
        available_departments = self.get_available_departments()
        
        return f"""
        You are an expert IT incident classifier. Analyze the incident description and provide classification.
        
        Incident Description: "{description}"
        
        Available Departments: {', '.join(available_departments)}
        
        Instructions:
        1. Classify the incident into one of these categories:
           - Network Issue, Hardware Problem, Software Issue, Security Problem, Email Issue, System Error, Database Issue, Server Issue, Password Reset, Account Issue (for IT department)
           - HR Query, Employee Issue, Leave Request, Payroll Issue, Benefits Question, Training Request (for HR department)  
           - Financial Query, Budget Issue, Invoice Problem, Expense Report, Payment Issue (for Finance department)
           - General Query, Facility Issue, Office Supply, Maintenance Request (for Admin department)
           - Unclassified (for unclear/inappropriate content)
        
        2. Determine severity: Low, Medium, or High based on business impact
        
        3. Provide a professional summary and email content
        
        Respond with ONLY valid JSON:
        {{
            "category": "exact category from list above",
            "severity": "Low|Medium|High",
            "title": "unique title",
            "summary": "brief professional summary",
            "email": "professional detailed email content for assigned staff"
        }}
        """

    def get_department_for_category(self, category: str) -> str:
        return self.category_department_mapping.get(category, "Admin")

    def create_fallback_response(self, reason: str) -> Dict[str, Any]:
        admin_staff = self.select_staff_from_department("Admin")
        
        if not admin_staff:
            return {
                "classification": {
                    "category": "Unclassified",
                    "severity": "Low",
                    "title":"Undefined",
                    "summary": "Incident could not be processed due to system limitations.",
                    "email": "This incident requires manual review."
                },
                "staff_assignment": {
                    "assigned_staff_email": None,
                    "assigned_staff_name": None,
                    "assigned_staff_id": None,
                    "assigned_department": "Admin",
                    "staff_skillset": None,
                    "assignment_status": "no_staff_available",
                    "assignment_reason": "No available staff in Admin department."
                },
                "processing_details": {
                    "fallback_reason": reason,
                    "department_available": False
                }
            }
        
        return {
            "classification": {
                "category": "Unclassified",
                "severity": "Low", 
                "title":"Undefined",
                "summary": f"Incident flagged for review: {reason}",
                "email": f"Dear {admin_staff['cr6dd_name']}, this incident requires manual review due to: {reason}. Please handle accordingly."
            },
            "staff_assignment": {
                "assigned_staff_email": admin_staff["cr6dd_email"],
                "assigned_staff_name": admin_staff["cr6dd_name"],
                "assigned_staff_id": admin_staff["cr6dd_id"],
                "assigned_department": "Admin",
                "staff_skillset": admin_staff["cr6dd_skillset"],
                "assignment_status": "assigned_fallback",
                "assignment_reason": f"Assigned to Admin due to: {reason}"
            },
            "processing_details": {
                "fallback_reason": reason,
                "department_available": True
            }
        }



    async def classify_incident(self, incident: IncidentRequest) -> Dict[str, Any]:
        try:
            start_time = datetime.now()
            description = incident.description.strip()
            
            if self.is_inappropriate_content(description):
                logger.warning(f"Inappropriate content detected: {description[:50]}...")
                result = self.create_fallback_response("Inappropriate content detected")
                result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
                result["timestamp"] = datetime.now()
                return result
            
            if self.is_ambiguous_description(description):
                logger.warning(f"Ambiguous description detected: {description}")
                result = self.create_fallback_response("Description too vague or unclear")
                result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
                result["timestamp"] = datetime.now()
                return result

            prompt = self.create_classification_prompt(description)
            
            messages = [
                {"role": "system", "content": "You are an expert incident classifier. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = await self.ai_client.create_chat_completion(
                messages=messages,
                temperature=0.2,
                max_tokens=400
            )

            ai_response = response['choices'][0]["message"]["content"].strip()
            
            if ai_response.startswith("```json"):
                ai_response = ai_response[7:-3]
            elif ai_response.startswith("```"):
                ai_response = ai_response[3:-3]

            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                ai_response = ai_response[json_start:json_end]
            
            classification_data = json.loads(ai_response)
            
            category = classification_data.get("category", "Unclassified")
            target_department = self.get_department_for_category(category)
            available_departments = self.get_available_departments()
            
            if target_department not in available_departments:
                logger.warning(f"Target department '{target_department}' not available. Falling back to Admin.")
                target_department = "Admin"
                
                if target_department not in available_departments:
                    logger.error("No departments have available staff!")
                    result = self.create_fallback_response("No available staff in any department")
                    result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
                    result["timestamp"] = datetime.now()
                    return result
            
            assigned_staff = self.select_staff_from_department(target_department)
            
            if not assigned_staff:
                logger.warning(f"No available staff in {target_department}. Trying Admin.")
                assigned_staff = self.select_staff_from_department("Admin")
                target_department = "Admin"
            
            if not assigned_staff:
                result = self.create_fallback_response("No available staff found")
                result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
                result["timestamp"] = datetime.now()
                return result
            
            return {
                "classification": {
                    "category": classification_data.get("category", "General Query"),
                    "severity": classification_data.get("severity", "Medium"),
                    "title":classification_data.get("title","Incident classification title"),
                    "summary": classification_data.get("summary", "Incident classification summary"),
                    "email": classification_data.get("email", "Incident assigned for review")
                },
                "staff_assignment": {
                    "assigned_staff_email": assigned_staff["cr6dd_email"],
                    "assigned_staff_name": assigned_staff["cr6dd_name"],
                    "assigned_staff_id": assigned_staff["cr6dd_staffid"],
                    "assigned_department": target_department,
                    "staff_skillset": assigned_staff["cr6dd_skillset"],
                    "assignment_status": "assigned",
                    "assignment_reason": f"Matched to {target_department} department based on incident category"
                },
                "processing_details": {
                    "department_match": target_department == self.get_department_for_category(category),
                    "fallback_used": target_department != self.get_department_for_category(category)
                },
                "timestamp": datetime.now()
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw AI response: {ai_response}")
            result = self.create_fallback_response("AI response parsing failed")
            result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
            result["timestamp"] = datetime.now()
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            result = self.create_fallback_response(f"System error: {str(e)}")
            result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)  
            result["timestamp"] = datetime.now()
            return result