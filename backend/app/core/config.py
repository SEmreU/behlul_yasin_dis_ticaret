from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API
    PROJECT_NAME: str = "Yasin Dış Ticaret İstihbarat API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 gün

    # External APIs - AI Providers (Birini seç!)
    OPENAI_API_KEY: Optional[str] = None  # Ücretli ama en iyi
    GROQ_API_KEY: Optional[str] = None  # BEDAVA ve hızlı! (Önerilen)
    HUGGINGFACE_API_KEY: Optional[str] = None  # Bedava
    ANTHROPIC_API_KEY: Optional[str] = None  # Ücretli
    
    # Other APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    RESEND_API_KEY: Optional[str] = None

    # SMTP (SendGrid yoksa bu kullanılır)
    SMTP_HOST: Optional[str] = None        # Örn: smtp.gmail.com
    SMTP_PORT: Optional[str] = "587"       # 587 (TLS) veya 465 (SSL)
    SMTP_USER: Optional[str] = None        # SMTP kullanıcı adı / email
    SMTP_PASSWORD: Optional[str] = None    # SMTP şifresi / uygulama şifresi
    FROM_EMAIL: Optional[str] = None       # Gönderici email adresi

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
