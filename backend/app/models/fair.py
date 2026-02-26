from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Date
from sqlalchemy.sql import func
from app.core.database import Base


class FairExhibitor(Base):
    """Fuar katılımcıları - Almanya, Çin vb. fuarlar"""
    __tablename__ = "fair_exhibitors"

    id = Column(Integer, primary_key=True, index=True)

    # Fuar bilgileri
    fair_name = Column(String(200), nullable=False, index=True)
    fair_location = Column(String(200))  # Şehir, Ülke
    fair_date = Column(Date, index=True)

    # Katılımcı firma
    company_name = Column(String(300), nullable=False, index=True)
    booth_number = Column(String(50))
    hall = Column(String(100))

    # İletişim
    country = Column(String(100), index=True)
    city = Column(String(100))
    website = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))

    # Ürün/Kategori
    product_categories = Column(JSON)  # Array of categories
    product_description = Column(Text)

    # Eşleşme skoru (kullanıcı ürünü ile)
    match_score = Column(Integer)  # 0-100
    matched_keywords = Column(JSON)  # Eşleşen anahtar kelimeler

    # Metadata
    logo_url = Column(String(500))
    extra_metadata = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
