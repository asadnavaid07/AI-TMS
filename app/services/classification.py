import json
from datetime import datetime
from fastapi import HTTPException
from app.models import IncidentRequest, AIClassificationResponse
from app.services.ai_service import GeminiClient
from app.utils.logging import logger

class AIClassificationService:
    def __init__(self):
        self.ai_cleint=GeminiClient()
        self.classification_prompt="""
        You are an expert IT incident analyst. Analyze the following incident and provide structured classification.
        
        Incident Title: {title}
        Description: {description}
        Reporter: {reporter_name} ({reporter_email})
        Department: {department}
        
        Analyze and respond with ONLY a valid JSON object containing:
        {{
            "category": "one of: IT Support, Network, Software, Hardware, Security, Access Control, General",
            "severity": "one of: Low, Medium, High, Critical",
            "confidence_score": float between 0.0 and 1.0,
            "summary": "concise 1-2 sentence summary",
            "estimated_resolution_time": "estimated time like '2-4 hours' or '1-2 days'",
            "assigned_team": "specific team name",
            "priority_score": integer between 1 and 10
        }}
        
        Consider:
        - Business impact and urgency
        - Technical complexity
        - Security implications
        - Resource requirements
        
        Respond ONLY with the JSON object, no additional text or formatting.
        """

    
    async def classify_incident(self,incident:IncidentRequest)->AIClassificationResponse:
        try:
            start_time=datetime.now()

            prompt=self.classification_prompt.format(
                title=incident.title,
                description=incident.description,
                reporter_name=incident.reporter_name,
                reporter_email=incident.reporter_email,
                department=incident.department or "Not specified"
            )

            messages=[
                {"role": "system", "content": "You are an expert IT incident classifier. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response=await self.ai_cleint.create_chat_completion(
                 messages=messages,
                temperature=0.3,
                max_tokens=500
            )

            ai_response=response['choices'][0]["message"]["content"].strip()

            if ai_response.startswith("```json"):
                ai_response = ai_response[7:-3]
            elif ai_response.startswith("```"):
                ai_response = ai_response[3:-3]
     
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                ai_response = ai_response[json_start:json_end]
            
            classification_data=json.loads(ai_response)
            classification=AIClassificationResponse(**classification_data)

            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"Classification completed in {processing_time:.2f}ms")
            
            return classification
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw AI response: {ai_response}")
            raise HTTPException(status_code=500, detail="AI response parsing failed")
        except Exception as e:
            logger.error(f"Classification error: {e}")
            raise HTTPException(status_code=500, detail=" error")


