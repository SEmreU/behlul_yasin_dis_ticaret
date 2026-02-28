from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum


class SubscriptionTier(str, enum.Enum):
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=True)  # nullable for Google OAuth users
    full_name = Column(Text)
    google_id = Column(Text, unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True, server_default="true")
    is_superuser = Column("is_admin", Boolean, default=False, server_default="false")

    subscription_tier = Column(
        Enum("FREE", "PRO", "ENTERPRISE", name="subscription_tier", create_type=False),
        default="FREE",
        server_default="FREE",
    )
    query_credits = Column(Integer, default=50, server_default="50")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    search_queries = relationship("SearchQuery", back_populates="user", cascade="all, delete-orphan")
    email_campaigns = relationship("EmailCampaign", back_populates="user", cascade="all, delete-orphan")
    chatbot_configs = relationship("ChatbotConfig", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")

