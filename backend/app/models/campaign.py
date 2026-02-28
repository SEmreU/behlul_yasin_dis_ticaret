from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    COMPLETED = "completed"
    PAUSED = "paused"


class EmailCampaign(Base):
    """Email kampanyaları - Toplu mail gönderimi"""
    __tablename__ = "email_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Kampanya sahibi
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Kampanya detayları
    name = Column(Text, nullable=False)
    subject = Column(Text)
    body_template = Column(Text)

    # Hedef kitle
    target_company_ids = Column(JSON)
    target_filters = Column(JSON)

    # Eklentiler
    attachments = Column(JSON)

    # İstatistikler
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)

    # Durum
    status = Column(
        Enum("draft", "scheduled", "sending", "completed", "paused", name="campaign_status", create_type=False),
        default="draft",
        server_default="draft",
        index=True,
    )

    # Zamanlama
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="email_campaigns")
    emails = relationship("CampaignEmail", back_populates="campaign", cascade="all, delete-orphan")


class CampaignEmail(Base):
    """Bireysel kampanya emailleri - tracking için"""
    __tablename__ = "campaign_emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    campaign_id = Column(UUID(as_uuid=True), ForeignKey("email_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), index=True)

    # Email detayları
    recipient_email = Column(Text, nullable=False)
    recipient_name = Column(Text)

    # Kişiselleştirilmiş içerik
    personalized_subject = Column(Text)
    personalized_body = Column(Text)

    # Tracking
    tracking_id = Column(Text, unique=True, index=True)

    is_sent = Column(Boolean, default=False)
    is_opened = Column(Boolean, default=False)
    is_clicked = Column(Boolean, default=False)
    is_bounced = Column(Boolean, default=False)

    sent_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    bounced_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    campaign = relationship("EmailCampaign", back_populates="emails")
    company = relationship("Company")
