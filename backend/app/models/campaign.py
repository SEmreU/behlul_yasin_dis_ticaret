from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
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

    id = Column(Integer, primary_key=True, index=True)

    # Kampanya sahibi
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Kampanya detayları
    name = Column(String(200), nullable=False)
    subject = Column(String(500), nullable=False)
    body_template = Column(Text, nullable=False)  # HTML/Text email body

    # Hedef kitle
    target_company_ids = Column(JSON)  # Array of company IDs
    target_filters = Column(JSON)  # Filtre kriterleri

    # Eklentiler
    attachments = Column(JSON)  # [{"name": "catalog.pdf", "url": "..."}]

    # İstatistikler
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)

    # Durum
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, index=True)

    # Zamanlama
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="email_campaigns")
    emails = relationship("CampaignEmail", back_populates="campaign", cascade="all, delete-orphan")


class CampaignEmail(Base):
    """Bireysel kampanya emailleri - tracking için"""
    __tablename__ = "campaign_emails"

    id = Column(Integer, primary_key=True, index=True)

    campaign_id = Column(Integer, ForeignKey("email_campaigns.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Email detayları
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(200))

    # Kişiselleştirilmiş içerik
    personalized_subject = Column(String(500))
    personalized_body = Column(Text)

    # Tracking
    sent_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    bounced_at = Column(DateTime(timezone=True))

    # Status
    is_sent = Column(Boolean, default=False)
    is_opened = Column(Boolean, default=False)
    is_clicked = Column(Boolean, default=False)
    is_bounced = Column(Boolean, default=False)

    # Tracking pixel/link
    tracking_id = Column(String(100), unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    campaign = relationship("EmailCampaign", back_populates="emails")
    company = relationship("Company")
