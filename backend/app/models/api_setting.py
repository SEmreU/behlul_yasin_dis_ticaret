from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ApiSetting(Base):
    """API anahtarlarını ve sistem ayarlarını saklayan model"""
    __tablename__ = "api_settings"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), unique=True, nullable=False, index=True)
    key_value = Column(Text, nullable=True)  # Şifreli saklanır
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # 'ai', 'maps', 'email', 'scraper', 'system'
    is_sensitive = Column(Boolean, default=True)  # Şifrelenmeli mi?
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ApiSetting {self.key_name}>"
