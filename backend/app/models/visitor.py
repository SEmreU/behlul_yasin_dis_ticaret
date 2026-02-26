from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class VisitorIdentification(Base):
    """Ziyaretçi kimliklendirme - Web sitesi tracking"""
    __tablename__ = "visitor_identifications"

    id = Column(Integer, primary_key=True, index=True)

    # Tracking bilgileri
    session_id = Column(String(100), unique=True, index=True)
    ip_address = Column(String(50), index=True)
    user_agent = Column(Text)
    referer = Column(String(500))

    # Lokasyon (GPS veya IP-based)
    latitude = Column(Float)
    longitude = Column(Float)
    location_source = Column(String(50))  # gps, ip_geolocation

    # Eşleşen firma
    identified_company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    confidence_score = Column(Float)  # 0-1 arası eşleşme skoru

    # Ek bilgiler
    country = Column(String(100))
    city = Column(String(100))

    # Fingerprinting
    browser_fingerprint = Column(String(200))

    # İzin durumu
    location_permission_granted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    identified_company = relationship("Company", back_populates="visitor_identifications")
