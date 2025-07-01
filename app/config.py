import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    title: str = "AI Incident Triage and Resolution Assistant"

    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    gemini_model: str = "gemini-1.5-flash" 

    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()

