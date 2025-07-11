from openai import AsyncAzureOpenAI
from typing import List, Dict, Any
from config import settings
from utils.logging import logger

class AzureClient:
    def __init__(self):
        self._configure_client()

    def _configure_client(self):
        if not settings.azure_api_key:
            raise ValueError("AZURE_API_KEY environment variable is required")
        if not settings.azure_endpoint:
            raise ValueError("AZURE_ENDPOINT environment variable is required")

        self.client = AsyncAzureOpenAI(
            api_version=settings.azure_api_version,
            azure_endpoint=settings.azure_endpoint,
            api_key=settings.azure_api_key,
        )
        self.model = settings.azure_model
        logger.info(f"Azure client configured with model: {self.model}")

    async def create_chat_completion(self, messages: List[Dict[str, str]], 
                                   temperature: float = 1.0,
                                   max_tokens: int = 4096) -> Any:
        try:
            response = await self.client.chat.completions.create(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1.0,
                model=self.model
            )
            return self._convert_response_format(response)
            
        except Exception as e:
            logger.error(f"Azure API error: {e}")
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
            return {
                "choices": [{
                    "message": {
                        "content": response.choices[0].message.content,
                        "role": "assistant"
                    },
                    "finish_reason": response.choices[0].finish_reason
                }],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logger.error(f"Error converting Azure response: {e}")
            return {
                "choices": [{
                    "message": {
                        "content": "Error processing response",
                        "role": "assistant"
                    },
                    "finish_reason": "error"
                }]
            }