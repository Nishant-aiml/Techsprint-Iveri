"""
Application Configuration Settings
====================================
GOOGLE TECHNOLOGIES CONFIGURATION:
- Google Gemini 2.5 Flash AI (Primary AI Engine via Google AI Studio API)
- Google Firebase Authentication & Admin SDK
- Google Cloud Platform Services (Cloud Storage, Cloud Vision)
- Google Sign-In OAuth 2.0 Integration

AI Model Priority:
  1. Google Gemini 2.5 Flash (Primary - Best performance)
  2. OpenAI GPT-5 Nano (Fallback)
  3. OpenAI GPT-5 Mini (Last resort)
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

# DEBUG: Print env vars at module load time
print(f"[DEBUG] OPENAI_API_KEY in os.environ: {'OPENAI_API_KEY' in os.environ}")
print(f"[DEBUG] OPENAI_API_KEY value exists: {bool(os.environ.get('OPENAI_API_KEY'))}")

class Settings(BaseSettings):
    # MongoDB (supports both MONGODB_URL and MONGODB_URI)
    MONGODB_URL: Optional[str] = None
    MONGODB_URI: Optional[str] = None  # Alternative name for compatibility
    MONGODB_DB_NAME: str = "smart_approval_ai"
    
    # Google Gemini (PRIMARY - Free Tier)
    GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")
    GEMINI_MODEL: str = "gemini-2.5-flash"  # Primary AI model - Gemini 2.5 Flash (free tier, fast)
    
    # OpenAI (Fallback when Gemini unavailable)
    # CRITICAL: Use os.environ.get as default to ensure Railway env vars are read
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL_PRIMARY: str = "gpt-5-nano"  # Fallback model - GPT-5 Nano (fast, lightweight)
    OPENAI_MODEL_FALLBACK: str = "gpt-5-mini"  # Last resort fallback - GPT-5 Mini
    
    # Firebase
    FIREBASE_PROJECT_ID: Optional[str] = os.environ.get("FIREBASE_PROJECT_ID")
    FIREBASE_STORAGE_BUCKET: Optional[str] = None  # Firebase Storage bucket name
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None  # Path to service account JSON
    
    # Database
    DATABASE_URL: Optional[str] = None  # PostgreSQL connection string (Supabase) or SQLite fallback
    
    # Unstructured-IO
    UNSTRUCTURED_API_KEY: Optional[str] = None
    UNSTRUCTURED_LOCAL: bool = True
    
    # Storage
    UPLOAD_DIR: str = "storage/uploads"
    REPORTS_DIR: str = "storage/reports"
    EVIDENCE_DIR: str = "storage/evidence"
    # Maximum single file size (safety limit) - 50 MB
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    
    # Processing
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.7
    EXTRACTION_RETRY_LIMIT: int = 3
    CHUNK_SIZE: int = 4000
    CHUNK_OVERLAP: int = 200
    
    # API Security
    API_TOKEN: Optional[str] = None
    
    class Config:
        # Try to find .env file, but don't require it
        env_file = ".env" if Path(".env").exists() else None
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Debug output
        print(f"[DEBUG] After Settings init, OPENAI_API_KEY is set: {bool(self.OPENAI_API_KEY)}")
        
        # Use MONGODB_URI if MONGODB_URL is not set
        if not self.MONGODB_URL and self.MONGODB_URI:
            self.MONGODB_URL = self.MONGODB_URI
        elif not self.MONGODB_URL:
            self.MONGODB_URL = "mongodb://localhost:27017/"

settings = Settings()
print(f"[DEBUG] Final settings.OPENAI_API_KEY is set: {bool(settings.OPENAI_API_KEY)}")


