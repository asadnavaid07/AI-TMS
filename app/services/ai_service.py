import google.generativeai as genai
from typing import List, Dict, Any
from app.config import settings
from app.utils.logging import logger


class GeminiClient:
    def __init__(self):
        self._configure_client()

    
    def _configure_client(self):
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"Gemini client configured with model: {settings.gemini_model}")
    
    async def create_chat_completion(self, messages: List[Dict[str, str]], 
                                   temperature: float = 0.3, 
                                   max_tokens: int = 500) -> Any:

        try:
            prompt = self._convert_messages_to_prompt(messages)

            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                candidate_count=1,
            )
    
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            return self._convert_response_format(response)
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"Instructions: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    def _convert_response_format(self, response) -> Dict[str, Any]:

        try:
            text_content = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "choices": [{
                    "message": {
                        "content": text_content,
                        "role": "assistant"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,  
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
        except Exception as e:
            logger.error(f"Error converting Gemini response: {e}")
            return {
                "choices": [{
                    "message": {
                        "content": "Error processing response",
                        "role": "assistant"
                    },
                    "finish_reason": "error"
                }]
            }