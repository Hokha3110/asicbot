import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Kali0t"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # JWT Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    GOOGLE_ADMIN_EMAILS: str = ""
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Database
    DATABASE_URL: str = "sqlite:///./security_copilot.db"
    
    # File Storage (Hybrid: Linux Server + Google Drive)
    UPLOAD_DIR: str = "./uploaded_docs"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # Google Drive Cloud Integration
    GOOGLE_DRIVE_ENABLED: bool = True
    GOOGLE_DRIVE_FOLDER_ID: str = "1vk4wIUrIXJ7LwlTluoyhq8h2w4Dpc0Ra"
    GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON: str = "" # raw JSON or path to service_account.json
    GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH: str = "./service_account.json"
    
    # AI Engine
    DEFAULT_LLM_PROVIDER: str = "gemini" # "gemini", "openai", "ollama", "mock"
    
    # Google Gemini Config (Pre-configured)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # OpenAI Config
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    
    EMBEDDING_PROVIDER: str = "sentence-transformers" # "sentence-transformers" or "openai"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://*.vercel.app,*"

    @property
    def cors_origin_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def google_admin_email_list(self) -> List[str]:
        return [email.strip().lower() for email in self.GOOGLE_ADMIN_EMAILS.split(",") if email.strip()]

    class Config:
        # Support running from the repository root or from the backend directory.
        env_file = (".env", "../.env")
        extra = "ignore"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
