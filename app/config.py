import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    title: str = "AI Incident Triage and Resolution Assistant"

    azure_api_key: Optional[str] = os.getenv("AZURE_API_KEY")
    azure_endpoint: Optional[str] = os.getenv("AZURE_ENDPOINT", "https://openai-anazim.openai.azure.com/")
    azure_api_version: str = "2024-12-01-preview"
    azure_model: str = "gpt-4o"

    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()