from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class UserActivity(Base):
    """Kullanıcı modül bazlı kullanım aktivite logu"""
    __tablename__ = "user_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Kullanıcı
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Modül bilgisi
    module = Column(Text, nullable=False, index=True)

    action = Column(Text)

    # İstek/yanıt özeti
    detail = Column(JSON)

    ip_address = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    user = relationship("User", back_populates="activities")
