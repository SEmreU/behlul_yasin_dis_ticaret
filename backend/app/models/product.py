from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    """Ürün bilgileri - GTIP kodları, OEM kodları, çoklu dil açıklamaları"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    # Ürün kodları
    gtip_code = Column(String(20), index=True)  # GTIP/HS Code
    oem_code = Column(String(100), index=True)  # OEM/Part number

    # Çoklu dil açıklamaları
    descriptions = Column(JSON)  # {"tr": "...", "en": "...", "de": "..."}

    # Kategoriler
    category = Column(String(200))
    subcategory = Column(String(200))

    # Ürün resmi
    image_url = Column(String(500))

    # Metadata
    extra_metadata = Column(JSON)  # Ek bilgiler

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
