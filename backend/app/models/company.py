from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    country = Column(String, index=True)
    city = Column(String)
    address = Column(Text)

    website = Column(String)
    phone = Column(String)
    email = Column(String)

    # Contact emails (purchasing, manager, sales)
    contact_emails = Column(JSON)  # Array of emails

    # Geolocation
    latitude = Column(Float)
    longitude = Column(Float)

    # Source of data
    source = Column(String)  # google_maps, alibaba, fair, manual

    # Additional metadata
    extra_metadata = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    visitor_identifications = relationship("VisitorIdentification", back_populates="identified_company")
