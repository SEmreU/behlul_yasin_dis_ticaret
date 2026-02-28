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
    """Tüm sistem ayarlarını listele (sadece superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")

    query = db.query(ApiSetting)
    if category:
        query = query.filter(ApiSetting.category == category)
    
    settings = query.order_by(ApiSetting.category, ApiSetting.key_name).all()
    
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
    """Bir ayarı güncelle (sadece superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    # Sadece izin verilen key isimlerine güncelleme yapılabilir
    allowed_keys = {s["key_name"] for s in DEFAULT_SETTINGS}
    if key_name not in allowed_keys:
        raise HTTPException(status_code=400, detail="Geçersiz ayar anahtarı")
    
    setting = db.query(ApiSetting).filter(ApiSetting.key_name == key_name).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"Ayar bulunamadı: {key_name}")
    
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
    """API bağlantısını test et (sadece superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
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
    """Tüm servislerin sağlık durumu (sadece superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
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
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
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


# ─────────────────────────────────────────────────────────────
# KULLANICI YÖNETİMİ
# ─────────────────────────────────────────────────────────────

class UserUpdateRequest(BaseModel):
    query_credits: Optional[int] = None
    subscription_tier: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
):
    """Tüm kullanıcıları listele (superuser gerekli)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    q = db.query(User)
    if search:
        q = q.filter(User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%"))
    
    users = q.order_by(User.id.desc()).offset(skip).limit(limit).all()
    total = db.query(User).count()
    
    return {
        "total": total,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "is_superuser": u.is_superuser,
                "subscription_tier": u.subscription_tier,
                "query_credits": u.query_credits,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "google_id": u.google_id,
            }
            for u in users
        ]
    }


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Kullanıcı bilgilerini güncelle (superuser gerekli)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    if data.query_credits is not None:
        user.query_credits = data.query_credits
    if data.subscription_tier is not None:
        user.subscription_tier = data.subscription_tier
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_superuser is not None:
        user.is_superuser = data.is_superuser
    
    db.commit()
    return {"status": "updated", "user_id": user_id}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Kullanıcıyı sil (superuser gerekli)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Kendinizi silemezsiniz")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    db.delete(user)
    db.commit()
    return {"status": "deleted", "user_id": user_id}


# ─────────────────────────────────────────────────────────────
# İSTATİSTİKLER
# ─────────────────────────────────────────────────────────────

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Sistem istatistikleri (superuser gerekli)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    
    from app.models.visitor import VisitorIdentification
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    today = now - timedelta(days=1)
    this_week = now - timedelta(days=7)
    this_month = now - timedelta(days=30)
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    new_today = db.query(User).filter(User.created_at >= today).count()
    
    total_visitors = db.query(VisitorIdentification).count()
    visitors_today = db.query(VisitorIdentification).filter(
        VisitorIdentification.created_at >= today
    ).count()
    visitors_week = db.query(VisitorIdentification).filter(
        VisitorIdentification.created_at >= this_week
    ).count()
    
    # Abonelik dağılımı
    tiers = db.query(
        User.subscription_tier, func.count(User.id)
    ).group_by(User.subscription_tier).all()
    tier_dist = {t: c for t, c in tiers}

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "new_today": new_today,
        },
        "visitors": {
            "total": total_visitors,
            "today": visitors_today,
            "this_week": visitors_week,
        },
        "subscription_distribution": tier_dist,
    }


# ─────────────────────────────────────────────────────────────
# KULLANICI AKTİVİTE / KULLANIM TAKİBİ
# ─────────────────────────────────────────────────────────────

@router.get("/users/{user_id}/activity")
def get_user_activity(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 100,
    module: Optional[str] = None,
):
    """
    Belirli bir kullanıcının aktivite geçmişi (superuser gerekli).
    Hangi modülü ne zaman, kaç kez ve başarıyla mı kullandığını gösterir.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")

    from app.models.activity import UserActivity
    from sqlalchemy import func

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    q = db.query(UserActivity).filter(UserActivity.user_id == user_id)
    if module:
        q = q.filter(UserActivity.module == module)

    activities = q.order_by(UserActivity.created_at.desc()).limit(limit).all()

    # Modül bazlı özet
    summary = db.query(
        UserActivity.module,
        func.count(UserActivity.id).label("count"),
        func.sum(UserActivity.credits_used).label("total_credits"),
        func.max(UserActivity.created_at).label("last_used"),
    ).filter(
        UserActivity.user_id == user_id,
        UserActivity.status == "success"
    ).group_by(UserActivity.module).all()

    # SearchQuery tablosundan da istatistik çek (eski data)
    from app.models.search_query import SearchQuery
    search_summary = db.query(
        SearchQuery.query_type,
        func.count(SearchQuery.id).label("count"),
        func.sum(SearchQuery.credits_used).label("total_credits"),
    ).filter(SearchQuery.user_id == user_id).group_by(SearchQuery.query_type).all()

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription_tier": user.subscription_tier,
            "query_credits": user.query_credits,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "module_summary": [
            {
                "module": s.module,
                "count": s.count,
                "total_credits": s.total_credits or 0,
                "last_used": s.last_used.isoformat() if s.last_used else None,
            } for s in summary
        ],
        "search_history": [
            {
                "query_type": s.query_type,
                "count": s.count,
                "total_credits": s.total_credits or 0,
            } for s in search_summary
        ],
        "recent_activities": [
            {
                "id": a.id,
                "module": a.module,
                "action": a.action,
                "credits_used": a.credits_used,
                "status": a.status,
                "meta_data": a.meta_data,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            } for a in activities
        ],
        "total_activities": q.count(),
    }


@router.get("/activity/feed")
def get_activity_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 50,
    module: Optional[str] = None,
):
    """
    Tüm kullanıcıların son aktivitelerini göster (global feed).
    Kim, ne zaman, hangi modülü kullandı?
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")

    from app.models.activity import UserActivity

    q = db.query(UserActivity, User).join(User, UserActivity.user_id == User.id)
    if module:
        q = q.filter(UserActivity.module == module)

    results = q.order_by(UserActivity.created_at.desc()).limit(limit).all()

    return {
        "feed": [
            {
                "activity_id": a.id,
                "module": a.module,
                "action": a.action,
                "credits_used": a.credits_used,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "user": {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                }
            } for a, u in results
        ]
    }


@router.get("/stats/modules")
def get_module_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Modül bazlı kullanım istatistikleri (hangi modül toplam kaç kez kullanıldı).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")

    from app.models.activity import UserActivity
    from sqlalchemy import func

    module_stats = db.query(
        UserActivity.module,
        func.count(UserActivity.id).label("total_uses"),
        func.count(func.distinct(UserActivity.user_id)).label("unique_users"),
        func.sum(UserActivity.credits_used).label("total_credits"),
    ).filter(
        UserActivity.status == "success"
    ).group_by(UserActivity.module).order_by(
        func.count(UserActivity.id).desc()
    ).all()

    # SearchQuery'den de ekle
    from app.models.search_query import SearchQuery
    search_stats = db.query(
        SearchQuery.query_type,
        func.count(SearchQuery.id).label("total_uses"),
        func.count(func.distinct(SearchQuery.user_id)).label("unique_users"),
        func.sum(SearchQuery.credits_used).label("total_credits"),
    ).group_by(SearchQuery.query_type).all()

    return {
        "module_stats": [
            {
                "module": s.module,
                "total_uses": s.total_uses,
                "unique_users": s.unique_users,
                "total_credits": s.total_credits or 0,
            } for s in module_stats
        ],
        "search_stats": [
            {
                "query_type": s.query_type,
                "total_uses": s.total_uses,
                "unique_users": s.unique_users,
                "total_credits": s.total_credits or 0,
            } for s in search_stats
        ],
    }
