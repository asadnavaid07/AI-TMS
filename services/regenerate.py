from models.requests import RegenerateRequest
from datetime import datetime
from services.ai_service import AzureClient
import json
from datetime import datetime
from fastapi import HTTPException
from utils.logging import logger



class AIRegenerator():
    def __init__(self):
        self.ai_client=AzureClient()
        self.prompt = """
Improve the following text by:
1. Making the summary more clear and structured.
2. Enhancing the tone to be professional, polite, and suitable for an email.
3. Correcting grammar, punctuation, and flow where needed.
Keep it concise but informative.

Summary:
{summary}

Email:
{email}
"""
    
    
    async def regenerate(self,regenerate:RegenerateRequest):
        try:
            start_time = datetime.now()

            prompt=self.prompt.format(
                summary=regenerate.summary,
                email=regenerate.email
            )

            messages=[
                {"role":"system","content":"You are an expert IT incident classifier and staff assignment specialist.Respond only with valid JSON."},
                {"role":"user","content":prompt}
            ]

            response=await self.ai_client.create_chat_completion(messages=messages,
                temperature=0.3,
                max_tokens=500)
            
            ai_response=response['choices'][0]['message']['content'].strip()
            if ai_response.startswith("```json"):
                ai_response = ai_response[7:-3]
            elif ai_response.startswith("```"):
                ai_response = ai_response[3:-3]

            parsed = json.loads(ai_response)
            
            if "summary" not in parsed or "email" not in parsed:
             raise HTTPException(status_code=400, detail="AI response is missing required fields.")

            return {
            "summary": parsed["summary"],
            "email": parsed["email"]["body"]
        }

        except json.JSONDecodeError as e:
         logger.error(f"JSON parsing error: {e}")
         logger.error(f"Raw AI response: {ai_response}")
         raise HTTPException(status_code=500, detail="AI response parsing failed")

        except Exception as e:
         logger.error(f"Regenerate error: {e}")
         raise HTTPException(status_code=500, detail="Regeneration service error")