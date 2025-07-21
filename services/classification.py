import json
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException
from models.requests import IncidentRequest
from .skill_indexer import SkillIndexer
from .content_validators import ContentValidator
from .staff_selector import StaffSelector
from .response_builder import ResponseBuilder
from .ai_service import AzureClient
from config import AI_TEMPERATURE, AI_MAX_TOKENS, DEFAULT_FALLBACK_DEPARTMENT, DEFAULT_FALLBACK_SKILLS
from utils.types import ClassificationResponse
from utils.logging import logger

class AIClassificationService:
    def __init__(self):
        self.ai_client = AzureClient()
        self.skill_indexer = SkillIndexer()
        self.content_validator = ContentValidator()
        self.staff_selector = StaffSelector()
        self.response_builder = ResponseBuilder(self.staff_selector)

    def create_classification_prompt(self, description: str) -> str:
        """Creates a prompt for AI to classify incidents and match to skills."""
        available_departments = self.skill_indexer.get_available_departments()
        skills_list = list(self.skill_indexer.skill_index.keys())
        
        return f"""
        You are an expert incident classifier for a company with specialized departments. Analyze the incident description and classify it based on the required skills and department expertise.

        Incident Description: "{description}"

        Available Departments: {', '.join(available_departments)}
        Available Skills: {', '.join(skills_list)}

        Instructions:
        1. Identify the key skills or expertise required to resolve the incident.
        2. Match the incident to the most relevant department based on the skills needed.
        3. If the department mentioned is not in the available departments, classify it as "Manual Assignment Required" and assign to Admin.
        4. Determine severity: Low, Medium, or High based on business impact.
        5. Provide a professional summary and email content for the assigned staff.
        6. Only classify as "Unclassified" if the description is inappropriate or too vague.

        Respond with ONLY valid JSON:
        {{
            "category": "specific issue type or 'Manual Assignment Required' or 'Unclassified'",
            "severity": "Low|Medium|High",
            "department": "matched department or 'Admin'",
            "required_skills": ["list of relevant skills"],
            "title": "unique title",
            "summary": "brief professional summary",
            "email": "professional detailed email content for assigned staff"
        }}
        """

    async def classify_incident(self, incident: IncidentRequest) -> ClassificationResponse:
        """Classifies an incident and assigns it to the appropriate staff."""
        try:
            start_time = datetime.now()
            description = incident.description.strip()

            if self.content_validator.is_inappropriate_content(description):
                logger.warning(f"Inappropriate content detected: {description[:50]}...")
                result = self.response_builder.create_fallback_response("Inappropriate content detected", is_unclassified=True)
            elif self.content_validator.is_ambiguous_description(description):
                logger.warning(f"Ambiguous description detected: {description}")
                result = self.response_builder.create_fallback_response("Description too vague or unclear", is_unclassified=True)
            else:
                prompt = self.create_classification_prompt(description)
                messages = [
                    {"role": "system", "content": "You are an expert incident classifier. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ]

                response = await self.ai_client.create_chat_completion(
                    messages=messages,
                    temperature=AI_TEMPERATURE,
                    max_tokens=AI_MAX_TOKENS
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
                category = classification_data.get("category", "Manual Assignment Required")
                target_department = classification_data.get("department", DEFAULT_FALLBACK_DEPARTMENT)
                required_skills = classification_data.get("required_skills", DEFAULT_FALLBACK_SKILLS)

                available_departments = self.skill_indexer.get_available_departments()
                if target_department not in available_departments:
                    logger.warning(f"Non-existent department '{target_department}' detected: {description[:50]}. Routing to {DEFAULT_FALLBACK_DEPARTMENT} for manual assignment.")
                    category = "Manual Assignment Required"
                    target_department = DEFAULT_FALLBACK_DEPARTMENT
                    required_skills = DEFAULT_FALLBACK_SKILLS

                assigned_staff = self.staff_selector.select_best_staff(required_skills, target_department)
                if not assigned_staff:
                    logger.warning(f"No available staff in {target_department}. Trying {DEFAULT_FALLBACK_DEPARTMENT}.")
                    category = "Manual Assignment Required"
                    assigned_staff = self.staff_selector.select_best_staff(DEFAULT_FALLBACK_SKILLS, DEFAULT_FALLBACK_DEPARTMENT)
                    target_department = DEFAULT_FALLBACK_DEPARTMENT

                if not assigned_staff:
                    result = self.response_builder.create_fallback_response("No available staff found", is_unclassified=False)
                else:
                    result = self.response_builder.create_classification_response(
                        classification_data=classification_data,
                        assigned_staff=assigned_staff,
                        target_department=target_department,
                        required_skills=required_skills,
                        original_department=classification_data.get("department", DEFAULT_FALLBACK_DEPARTMENT)
                    )

            result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
            result["timestamp"] = datetime.now().isoformat()
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw AI response: {ai_response}")
            result = self.response_builder.create_fallback_response(f"AI response parsing failed", is_unclassified=True)
            result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
            result["timestamp"] = datetime.now().isoformat()
            return result

        except Exception as e:
            logger.error(f"Classification error: {e}")
            result = self.response_builder.create_fallback_response(f"System error: {str(e)}", is_unclassified=True)
            result["processing_time_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
            result["timestamp"] = datetime.now().isoformat()
            return result