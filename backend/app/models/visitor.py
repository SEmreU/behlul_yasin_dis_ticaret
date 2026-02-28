from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class VisitorIdentification(Base):
    """Ziyaretçi kimliklendirme - Web sitesi tracking"""
    __tablename__ = "visitor_identifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tracking bilgileri
    session_id = Column(Text, unique=True, index=True)
    ip_address = Column(Text, index=True)
    user_agent = Column(Text)
    referer = Column(Text)

    # Lokasyon
    latitude = Column(Float)
    longitude = Column(Float)
    location_source = Column(Text)

    # Eşleşen firma
    identified_company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), index=True)
    confidence_score = Column(Float)

    # Fingerprinting
    browser_fingerprint = Column(Text)

    location_permission_granted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    identified_company = relationship("Company", back_populates="visitor_identifications")
