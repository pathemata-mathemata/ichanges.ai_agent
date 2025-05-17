# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SONAR_API_KEY: str = os.getenv("SONAR_API_KEY")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

settings = Settings()