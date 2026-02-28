from sqlalchemy import Column, String, Text, JSON, DateTime, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class FairExhibitor(Base):
    """Fuar katılımcıları"""
    __tablename__ = "fair_exhibitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Fuar bilgileri
    fair_name = Column(Text, nullable=False, index=True)
    fair_location = Column(Text)
    fair_date = Column(Date, index=True)

    # Katılımcı firma
    company_name = Column(Text, nullable=False, index=True)
    booth_number = Column(Text)
    hall = Column(Text)

    # İletişim
    country = Column(Text, index=True)
    city = Column(Text)
    website = Column(Text)
    email = Column(Text)
    phone = Column(Text)

    # Ürün/Kategori
    product_categories = Column(JSON)
    product_description = Column(Text)

    # Eşleşme skoru
    match_score = Column(Integer)
    matched_keywords = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
