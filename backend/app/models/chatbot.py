from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ChatbotGoal(str, enum.Enum):
    """Chatbot hedefi"""
    EMAIL = "email"
    PHONE = "phone"
    BOTH = "both"


class ChatbotConfig(Base):
    """Chatbot konfigürasyonu"""
    __tablename__ = "chatbot_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Bot ayarları
    bot_name = Column(String(100), default="TradeBot")
    welcome_message = Column(Text, nullable=False)
    supported_languages = Column(JSON, default=["tr", "en"])  # ["tr", "en", "de", ...]
    goal = Column(SQLEnum(ChatbotGoal), default=ChatbotGoal.BOTH)
    
    # Şirket bilgileri
    company_info = Column(JSON, nullable=True)  # {"name": "...", "products": "...", "website": "..."}
    
    # Embed code
    embed_code = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # İlişkiler
    user = relationship("User", back_populates="chatbot_configs")
    conversations = relationship("ChatbotConversation", back_populates="config", cascade="all, delete-orphan")


class ChatbotConversation(Base):
    """Chatbot konuşmaları"""
    __tablename__ = "chatbot_conversations"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("chatbot_configs.id"), nullable=False)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Konuşma verileri
    messages = Column(JSON, default=[])  # [{"role": "user", "content": "...", "timestamp": "..."}, ...]
    collected_data = Column(JSON, default={})  # {"email": "...", "phone": "...", "name": "...", "inquiry": "..."}
    
    # Dil
    detected_language = Column(String(10), default="tr")
    
    # Status
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # İlişkiler
    config = relationship("ChatbotConfig", back_populates="conversations")
    lead = relationship("ChatbotLead", back_populates="conversation", uselist=False)


class ChatbotLead(Base):
    """Chatbot'tan toplanan lead'ler"""
    __tablename__ = "chatbot_leads"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chatbot_conversations.id"), nullable=False, unique=True)
    
    # Lead bilgileri
    name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(200), nullable=True)
    inquiry = Column(Text, nullable=True)  # Ne arıyor?
    
    # Metadata
    language = Column(String(10), default="tr")
    source_url = Column(String(500), nullable=True)  # Hangi sayfadan geldi
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # İlişkiler
    conversation = relationship("ChatbotConversation", back_populates="lead")
