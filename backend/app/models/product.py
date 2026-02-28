from sqlalchemy import Column, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Product(Base):
    """Ürün bilgileri"""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    gtip_code = Column(Text, index=True)
    oem_code = Column(Text, index=True)

    descriptions = Column(JSON)

    category = Column(Text)
    subcategory = Column(Text)

    image_url = Column(Text)

    metadata_ = Column("metadata", JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
