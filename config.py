import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
 
load_dotenv()

INAPPROPRIATE_PATTERNS = [
    r'\b(fuck|shit|damn|bitch|asshole|crap)\b',
    r'\b(hate|kill|die|murder|suicide)\b',
    r'\b(porn|sex|nude|naked)\b',
    r'\b(racist|sexist|homophobic)\b'
]

DEFAULT_FALLBACK_DEPARTMENT = "Admin"
DEFAULT_FALLBACK_SKILLS = ["general support"]
AI_TEMPERATURE = 0.2
AI_MAX_TOKENS = 400

class Settings(BaseSettings):
    title: str = "AI Incident Triage and Resolution Assistant"

    azure_api_key: Optional[str] = os.getenv("AZURE_API_KEY")
    azure_endpoint: Optional[str] = os.getenv("AZURE_ENDPOINT")
    azure_api_version: str = "2024-12-01-preview"
    azure_model: str = "gpt-4o"

    

    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"


settings = Settings()