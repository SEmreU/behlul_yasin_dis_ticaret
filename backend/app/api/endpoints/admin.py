from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import base64

from app.core.deps import get_db, get_current_active_user, get_current_superuser
from app.models.user import User
from app.models.api_setting import ApiSetting

router = APIRouter()

# Varsayılan ayarlar listesi (ilk kurulumda DB'ye yazılır)
DEFAULT_SETTINGS = [
    # AI Servisleri
    {"key_name": "GROQ_API_KEY", "description": "Groq AI API Key (Chatbot için - bedava)", "category": "ai", "is_sensitive": True},
    {"key_name": "OPENAI_API_KEY", "description": "OpenAI GPT-4 API Key (Görüntü arama için)", "category": "ai", "is_sensitive": True},
    {"key_name": "ANTHROPIC_API_KEY", "description": "Anthropic Claude API Key (opsiyonel)", "category": "ai", "is_sensitive": True},
    {"key_name": "HUGGINGFACE_API_KEY", "description": "HuggingFace API Key (opsiyonel)", "category": "ai", "is_sensitive": True},
    {"key_name": "AI_PROVIDER", "description": "Aktif AI sağlayıcı: groq, openai, anthropic, huggingface", "category": "ai", "is_sensitive": False},
    # Harita & Scraping
    {"key_name": "GOOGLE_MAPS_API_KEY", "description": "Google Maps Platform API Key (Harita modülü)", "category": "maps", "is_sensitive": True},
    {"key_name": "SCRAPERAPI_KEY", "description": "ScraperAPI Key (Web scraping için proxy)", "category": "scraper", "is_sensitive": True},
    {"key_name": "PROXY_URL", "description": "Proxy sunucu URL (örn: socks5://user:pass@host:port)", "category": "scraper", "is_sensitive": True},
    {"key_name": "PROXY_USERNAME", "description": "Proxy kullanıcı adı", "category": "scraper", "is_sensitive": True},
    {"key_name": "PROXY_PASSWORD", "description": "Proxy şifresi", "category": "scraper", "is_sensitive": True},
    # E-mail
    {"key_name": "SENDGRID_API_KEY", "description": "SendGrid API Key (mail gönderimi)", "category": "email", "is_sensitive": True},
    {"key_name": "SMTP_HOST", "description": "SMTP sunucu adresi (örn: smtp.gmail.com)", "category": "email", "is_sensitive": False},
    {"key_name": "SMTP_PORT", "description": "SMTP port (örn: 587)", "category": "email", "is_sensitive": False},
    {"key_name": "SMTP_USER", "description": "SMTP kullanıcı adı / e-mail", "category": "email", "is_sensitive": False},
    {"key_name": "SMTP_PASSWORD", "description": "SMTP şifresi", "category": "email", "is_sensitive": True},
    {"key_name": "FROM_EMAIL", "description": "Gönderici e-mail adresi", "category": "email", "is_sensitive": False},
    # Sistem
    {"key_name": "SECRET_KEY", "description": "JWT imzalama anahtarı (değiştirme!)", "category": "system", "is_sensitive": True},
    {"key_name": "MAX_SEARCH_RESULTS", "description": "Arama başına maksimum sonuç sayısı", "category": "system", "is_sensitive": False},
]


def _mask_value(value: str, is_sensitive: bool) -> str:
    """Hassas değerleri maskele: sk-abc...xyz"""
    if not value or not is_sensitive:
        return value
    if len(value) <= 8:
        return "••••••••"
    return value[:4] + "••••••••" + value[-4:]


def _encode_value(value: str) -> str:
    """Basit base64 encoding (production'da AES kullanın)"""
    return base64.b64encode(value.encode()).decode()


def _decode_value(encoded: str) -> str:
    """Base64 decode"""
    try:
        return base64.b64decode(encoded.encode()).decode()
    except Exception:
        return encoded


class SettingUpdate(BaseModel):
    key_value: str


class SettingResponse(BaseModel):
    key_name: str
    key_value: Optional[str]  # Maskeli değer
    description: Optional[str]
    category: Optional[str]
    is_sensitive: bool
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/settings", response_model=List[SettingResponse])
def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    category: Optional[str] = None
):
    """
    Tüm sistem ayarlarını listele (hassas değerler maskeli gösterilir)
    
    Query params:
    - category: ai, maps, email, scraper, system
    """
    query = db.query(ApiSetting)
    if category:
        query = query.filter(ApiSetting.category == category)
    
    settings = query.order_by(ApiSetting.category, ApiSetting.key_name).all()
    
    # Hiç ayar yoksa varsayılanları oluştur
    if not settings:
        _initialize_default_settings(db)
        settings = db.query(ApiSetting).all()
    
    result = []
    for s in settings:
        decoded = _decode_value(s.key_value) if s.key_value else None
        result.append(SettingResponse(
            key_name=s.key_name,
            key_value=_mask_value(decoded, s.is_sensitive) if decoded else None,
            description=s.description,
            category=s.category,
            is_sensitive=s.is_sensitive,
            is_active=s.is_active
        ))
    
    return result


@router.put("/settings/{key_name}")
def update_setting(
    key_name: str,
    data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Bir ayarı güncelle"""
    setting = db.query(ApiSetting).filter(ApiSetting.key_name == key_name).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"Ayar bulunamadı: {key_name}")
    
    # Encode edip kaydet
    setting.key_value = _encode_value(data.key_value) if data.key_value else None
    db.commit()
    
    return {"status": "updated", "key_name": key_name}


@router.get("/settings/{key_name}/value")
def get_setting_value(
    key_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Bir ayarın gerçek değerini döndür (sadece superuser için)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Bu işlem için admin yetkisi gereklidir")
    
    setting = db.query(ApiSetting).filter(ApiSetting.key_name == key_name).first()
    if not setting or not setting.key_value:
        return {"key_name": key_name, "value": None}
    
    return {"key_name": key_name, "value": _decode_value(setting.key_value)}


@router.post("/settings/test/{key_name}")
async def test_api_connection(
    key_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """API bağlantısını test et"""
    setting = db.query(ApiSetting).filter(ApiSetting.key_name == key_name).first()
    
    if not setting or not setting.key_value:
        return {"status": "error", "message": "API key girilmemiş"}
    
    value = _decode_value(setting.key_value)
    
    try:
        if key_name == "GROQ_API_KEY":
            from groq import Groq
            client = Groq(api_key=value)
            client.models.list()
            return {"status": "success", "message": "Groq bağlantısı başarılı ✅"}
        
        elif key_name == "OPENAI_API_KEY":
            from openai import OpenAI
            client = OpenAI(api_key=value)
            client.models.list()
            return {"status": "success", "message": "OpenAI bağlantısı başarılı ✅"}
        
        elif key_name == "GOOGLE_MAPS_API_KEY":
            import googlemaps
            gmaps = googlemaps.Client(key=value)
            gmaps.geocode("Istanbul")
            return {"status": "success", "message": "Google Maps bağlantısı başarılı ✅"}
        
        elif key_name == "SENDGRID_API_KEY":
            import sendgrid
            sg = sendgrid.SendGridAPIClient(api_key=value)
            sg.client.api_keys.get()
            return {"status": "success", "message": "SendGrid bağlantısı başarılı ✅"}
        
        else:
            return {"status": "info", "message": "Bu key için otomatik test mevcut değil"}
            
    except Exception as e:
        return {"status": "error", "message": f"Bağlantı hatası: {str(e)[:200]}"}


@router.get("/health")
async def system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Tüm servislerin sağlık durumu"""
    import redis as redis_lib
    from app.core.config import settings as cfg
    
    health = {
        "database": "unknown",
        "redis": "unknown",
        "groq_ai": "unknown",
        "openai": "unknown",
        "google_maps": "unknown",
    }
    
    # DB
    try:
        db.execute("SELECT 1")
        health["database"] = "✅ Bağlı"
    except Exception as e:
        health["database"] = f"❌ Hata: {str(e)[:50]}"
    
    # Redis
    try:
        r = redis_lib.from_url(cfg.REDIS_URL)
        r.ping()
        health["redis"] = "✅ Bağlı"
    except Exception as e:
        health["redis"] = f"❌ Hata: {str(e)[:50]}"
    
    # Groq
    groq_setting = db.query(ApiSetting).filter(ApiSetting.key_name == "GROQ_API_KEY").first()
    groq_key = _decode_value(groq_setting.key_value) if groq_setting and groq_setting.key_value else cfg.GROQ_API_KEY
    if groq_key:
        try:
            from groq import Groq
            Groq(api_key=groq_key).models.list()
            health["groq_ai"] = "✅ Bağlı"
        except Exception:
            health["groq_ai"] = "❌ Geçersiz key"
    else:
        health["groq_ai"] = "⚠️ Key girilmemiş"
    
    return health


def _initialize_default_settings(db: Session):
    """Varsayılan ayarları DB'ye yaz"""
    from app.core.config import settings as cfg
    
    # Env'den mevcut değerleri al
    env_values = {
        "GROQ_API_KEY": getattr(cfg, 'GROQ_API_KEY', None),
        "OPENAI_API_KEY": getattr(cfg, 'OPENAI_API_KEY', None),
        "AI_PROVIDER": "groq",
        "MAX_SEARCH_RESULTS": "50",
    }
    
    for s in DEFAULT_SETTINGS:
        existing = db.query(ApiSetting).filter(ApiSetting.key_name == s["key_name"]).first()
        if not existing:
            env_val = env_values.get(s["key_name"])
            new_setting = ApiSetting(
                key_name=s["key_name"],
                key_value=_encode_value(env_val) if env_val else None,
                description=s["description"],
                category=s["category"],
                is_sensitive=s["is_sensitive"],
            )
            db.add(new_setting)
    
    db.commit()


def get_setting_from_db(db: Session, key_name: str, fallback=None) -> Optional[str]:
    """Backend servisleri için: DB'den key oku, yoksa fallback"""
    setting = db.query(ApiSetting).filter(
        ApiSetting.key_name == key_name,
        ApiSetting.is_active == True
    ).first()
    
    if setting and setting.key_value:
        return _decode_value(setting.key_value)
    
    return fallback
