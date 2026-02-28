from sqlalchemy import Column, String, DateTime, Text, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, index=True)
    country = Column(Text, index=True)
    city = Column(Text)
    address = Column(Text)

    website = Column(Text)
    phone = Column(Text)
    email = Column(Text)

    # Contact emails (purchasing, manager, sales)
    contact_emails = Column(JSON)

    # Geolocation
    latitude = Column(Float)
    longitude = Column(Float)

    # Source of data
    source = Column(Text)

    # Additional metadata
    metadata_ = Column("metadata", JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    visitor_identifications = relationship("VisitorIdentification", back_populates="identified_company")
