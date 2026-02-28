from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum


class QueryType(str, enum.Enum):
    PRODUCT_SEARCH = "product_search"
    COMPANY_SEARCH = "company_search"
    MAP_SCRAPING = "map_scraping"
    FAIR_SEARCH = "fair_search"
    IMAGE_SEARCH = "image_search"


class SearchQuery(Base):
    """Kullanıcı aramalarının loglama ve kontör takibi"""
    __tablename__ = "search_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Kullanıcı ilişkisi
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Sorgu detayları
    query_type = Column(
        Enum("product_search", "company_search", "map_scraping", "fair_search", "image_search", "b2b_search", "contact_search",
             name="query_type", create_type=False),
        nullable=False, index=True,
    )
    query_parameters = Column(JSON)

    # Sonuçlar
    results_count = Column(Integer, default=0)
    results_data = Column(JSON)

    # Maliyet
    credits_used = Column(Integer, default=1)

    # Durum
    status = Column(
        Enum("pending", "completed", "failed", name="query_status", create_type=False),
        default="pending",
        server_default="pending",
    )
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="search_queries")
