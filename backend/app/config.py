# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SONAR_API_KEY: str = os.getenv("SONAR_API_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID: str = os.getenv("SEARCH_ENGINE_ID")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

settings = Settings()