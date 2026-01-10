"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # MongoDB (supports both MONGODB_URL and MONGODB_URI)
    MONGODB_URL: Optional[str] = None
    MONGODB_URI: Optional[str] = None  # Alternative name for compatibility
    MONGODB_DB_NAME: str = "smart_approval_ai"
    
    # Google Gemini (PRIMARY - Free Tier)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"  # Primary AI model - Gemini 2.5 Flash (free tier, fast)
    
    # OpenAI (Fallback when Gemini unavailable)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_PRIMARY: str = "gpt-5-nano"  # Fallback model - GPT-5 Nano (fast, lightweight)
    OPENAI_MODEL_FALLBACK: str = "gpt-5-mini"  # Last resort fallback - GPT-5 Mini
    
    # Firebase
    FIREBASE_PROJECT_ID: Optional[str] = None  # Firebase Project ID for token verification
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
        # Look for .env in multiple locations
        # Railway/Docker: current directory or /app
        # Local dev: project root (parent of backend)
        import os
        env_paths = [
            Path(__file__).parent.parent.parent / ".env",  # Project root
            Path(__file__).parent.parent / ".env",  # Backend directory
            Path(".env"),  # Current directory
        ]
        for p in env_paths:
            if p.exists():
                env_file = str(p)
                break
        else:
            env_file = None  # No .env file found - rely on OS environment
        
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env that aren't in the model
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use MONGODB_URI if MONGODB_URL is not set
        if not self.MONGODB_URL and self.MONGODB_URI:
            self.MONGODB_URL = self.MONGODB_URI
        elif not self.MONGODB_URL:
            self.MONGODB_URL = "mongodb://localhost:27017/"

settings = Settings()
