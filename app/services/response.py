import json
from fastapi import HTTPException
from app.models import IncidentRequest, AIClassificationResponse, AIResponseSuggestion
from app.services.ai_service import GeminiClient
from app.utils.logging import logger

class ResponseSuggestionService:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.response_prompt = """
        Based on the incident classification, generate a helpful response suggestion.
        
        Incident: {title}
        Category: {category}
        Severity: {severity}
        Summary: {summary}
        
        Provide a JSON response with:
        {{
            "suggested_response": "professional response to send to the user",
            "escalation_needed": boolean,
            "next_actions": ["action1", "action2", "action3"],
            "knowledge_base_articles": ["article1", "article2"]
        }}
        
        Make the response:
        - Professional and empathetic
        - Include estimated timeline
        - Provide clear next steps
        - Reference relevant documentation when applicable
        
        Respond ONLY with the JSON object, no additional text or formatting.
        """
    
    async def generate_response(self, incident: IncidentRequest, 
                              classification: AIClassificationResponse) -> AIResponseSuggestion:
        try:
            prompt = self.response_prompt.format(
                title=incident.title,
                category=classification.category,
                severity=classification.severity,
                summary=classification.summary
            )
            
            messages = [
                {"role": "system", "content": "You are an expert customer service representative. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.gemini_client.create_chat_completion(
                messages=messages,
                temperature=0.4,
                max_tokens=800
            )
            
            ai_response = response["choices"][0]["message"]["content"].strip()
            
            if ai_response.startswith("```json"):
                ai_response = ai_response[7:-3]
            elif ai_response.startswith("```"):
                ai_response = ai_response[3:-3]
            
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                ai_response = ai_response[json_start:json_end]
            
            response_data = json.loads(ai_response)
            return AIResponseSuggestion(**response_data)
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            raise HTTPException(status_code=500, detail="Response generation failed")
