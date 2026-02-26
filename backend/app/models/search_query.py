from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
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

    id = Column(Integer, primary_key=True, index=True)

    # Kullanıcı ilişkisi
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Sorgu detayları
    query_type = Column(Enum(QueryType), nullable=False, index=True)
    query_parameters = Column(JSON)  # Arama parametreleri

    # Sonuçlar
    results_count = Column(Integer, default=0)
    results_data = Column(JSON)  # Kısmi sonuç verisi (preview)

    # Maliyet
    credits_used = Column(Integer, default=1)

    # Durum
    status = Column(String(50), default="completed")  # completed, failed, pending
    error_message = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="search_queries")
