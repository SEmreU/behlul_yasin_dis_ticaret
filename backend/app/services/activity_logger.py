"""
Kullanıcı aktivite loglama servisi.
Her modül kendi endpoint'inden log_activity() çağırarak kullanım kaydeder.
"""
from sqlalchemy.orm import Session
from app.models.activity import UserActivity
from typing import Optional, Dict, Any


# Modül isimleri (frontend ile tutarlı olması için sabit)
class Module:
    SEARCH = "search"
    CHATBOT = "chatbot"
    MAPS = "maps"
    CONTACT = "contact"
    FAIRS = "fairs"
    MAIL = "mail"
    B2B = "b2b"
    VISITOR = "visitor"
    MARKETS = "markets"
    MARKETPLACE = "marketplace"
    SCRAPING = "scraping"


MODULE_LABELS = {
    Module.SEARCH: "Ürün Arama",
    Module.CHATBOT: "AI Chatbot",
    Module.MAPS: "Harita Araştırma",
    Module.CONTACT: "İletişim Bulucu",
    Module.FAIRS: "Fuar Analizi",
    Module.MAIL: "Otomatik Mail",
    Module.B2B: "B2B Platformlar",
    Module.VISITOR: "Ziyaretçi Takip",
    Module.MARKETS: "Pazar Analizi",
    Module.MARKETPLACE: "Marketplace",
    Module.SCRAPING: "Web Scraping",
}


def log_activity(
    db: Session,
    user_id: int,
    module: str,
    action: str,
    credits_used: int = 0,
    status: str = "success",
    meta_data: Optional[Dict[str, Any]] = None
) -> UserActivity:
    """
    Kullanıcı aktivitesini logla.
    
    Args:
        db: Database session
        user_id: Kullanıcı ID
        module: Modül adı (Module sınıfındaki sabitler)
        action: Yapılan işlem açıklaması
        credits_used: Harcanan kredi miktarı
        status: "success" | "error" | "pending"
        meta_data: Ek bilgiler (arama terimi, sonuç sayısı vb.)
    """
    activity = UserActivity(
        user_id=user_id,
        module=module,
        action=action,
        credits_used=credits_used,
        status=status,
        meta_data=meta_data or {}
    )
    db.add(activity)
    db.commit()
    return activity


def log_activity_safe(
    db: Session,
    user_id: int,
    module: str,
    action: str,
    credits_used: int = 0,
    status: str = "success",
    meta_data: Optional[Dict[str, Any]] = None
) -> None:
    """Hata durumunda sessizce geç (kritik endpoint'lerde kullan)"""
    try:
        log_activity(db, user_id, module, action, credits_used, status, meta_data)
    except Exception:
        pass
