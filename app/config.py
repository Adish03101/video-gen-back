import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ============================
    # 1. Server Settings
    # ============================
    PORT: int = 8000
    ENVIRONMENT: str = "development"  # 'development' or 'production'

    # ============================
    # 2. AI Provider Settings
    # ============================
    # Pydantic will automatically look for 'GROQ_API_KEY' in your .env file
    GROQ_API: str 
    
    # Default model if not specified in .env
    LLM_MODEL: str = "llama-3.3-70b-versatile" 

    class Config:
        # This tells Pydantic to read the .env file in the root folder
        env_file = ".env"
        env_file_encoding = "utf-8"
        # This allows you to have extra variables in .env without crashing
        extra = "ignore" 

# Initialize the settings once
settings = Settings()