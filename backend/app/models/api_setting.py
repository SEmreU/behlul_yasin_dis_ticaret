from sqlalchemy import Column, String, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class ApiSetting(Base):
    """API anahtarlarını ve sistem ayarlarını saklayan model"""
    __tablename__ = "api_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_name = Column(Text, unique=True, nullable=False, index=True)
    key_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    category = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ApiSetting {self.key_name}>"
