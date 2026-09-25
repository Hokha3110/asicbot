import os
import json
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Security Solution Copilot"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # JWT Security
    SECRET_KEY: str = "cyber-presales-sec-copilot-jwt-super-secret-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours

    # Google OAuth
    GOOGLE_CLIENT_ID: str = "222975697295-sjerq0nnb37r4ofc71tfl1pam1gi6g6q.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = "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"
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
    GOOGLE_DRIVE_FOLDER_ID: str = "1vk4wIUrIXJ7LwlTLuoyhq8h2w4Dpc0Ra"
    GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON: str = "" # raw JSON or path to service_account.json
    GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH: str = "./service_account.json"
    GOOGLE_DRIVE_TOKENS_PATH: str = "./google_drive_tokens.json"
    
    # AI Engine
    DEFAULT_LLM_PROVIDER: str = "gemini" # "gemini", "openai", "ollama", "mock"
    
    # Google Gemini Config (Pre-configured)
    GEMINI_API_KEY: str = "AQ.Ab8RN6JAnXhufiAAcj08P6O-Yee5C7LL2WYgBC5kIiD2Pcg79g"
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
        env_file = (".env", "../.env")
        extra = "ignore"

settings = Settings()

# Check and auto-load client credentials from service_account.json if present
for sa_path in [settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_PATH, "./service_account.json", "../service_account.json", "./backend/service_account.json"]:
    if os.path.exists(sa_path):
        try:
            with open(sa_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "web" in data:
                    web_info = data["web"]
                    if web_info.get("client_id"):
                        settings.GOOGLE_CLIENT_ID = web_info["client_id"]
                    if web_info.get("client_secret"):
                        settings.GOOGLE_CLIENT_SECRET = web_info["client_secret"]
        except Exception:
            pass
        break

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
