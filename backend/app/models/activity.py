from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserActivity(Base):
    """Kullanıcı modül bazlı kullanım aktivite logu"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)

    # Kullanıcı
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Modül bilgisi
    module = Column(String(100), nullable=False, index=True)
    # Örn: "search", "chatbot", "maps", "contact", "fairs", "mail", "b2b", "visitor"

    action = Column(String(200))
    # Örn: "product_search", "send_message", "scrape_map", "find_contact"

    # Kredi tüketimi
    credits_used = Column(Integer, default=0)

    # İstek/yanıt özeti
    meta_data = Column(JSON)
    # Örn: {"query": "...", "results": 5, "status": "success"}

    status = Column(String(20), default="success")  # success, error, pending

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    user = relationship("User", back_populates="activities")
