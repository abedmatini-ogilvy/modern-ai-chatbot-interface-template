"""
Configuration Management for Trend Research Backend

Loads environment variables and provides configuration settings
for the FastAPI application.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Trend Research API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS - Allow Next.js frontend
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "https://*.vercel.app",  # Vercel deployments
        "https://*.github.dev",  # Codespaces
        "https://*.githubpreview.dev",  # Codespaces preview
    ]
    
    # Azure OpenAI (for analysis and report generation)
    AZURE_AI_API_KEY: Optional[str] = os.getenv("AZURE_AI_API_KEY")
    AZURE_AI_ENDPOINT: Optional[str] = os.getenv("AZURE_AI_ENDPOINT")
    AZURE_AI_MODEL_NAME: str = os.getenv("AZURE_AI_MODEL_NAME", "gpt-4")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Session Management
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    MAX_CONCURRENT_SESSIONS: int = int(os.getenv("MAX_CONCURRENT_SESSIONS", "100"))
    
    # Research Settings
    DEFAULT_MAX_RESULTS: int = 50
    RESEARCH_TIMEOUT_SECONDS: int = 300  # 5 minutes max per research
    
    @property
    def azure_openai_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured"""
        return bool(self.AZURE_AI_API_KEY and self.AZURE_AI_ENDPOINT)


# Global settings instance
settings = Settings()
