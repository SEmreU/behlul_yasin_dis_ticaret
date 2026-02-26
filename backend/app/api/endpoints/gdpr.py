"""GDPR/KVKK Uyumlu Veri Yönetimi Endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.company import Company
from app.models.search_query import SearchQuery
from app.models.visitor import VisitorIdentification

router = APIRouter()


@router.get("/my-data")
def get_my_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    GDPR Madde 15: Kullanıcının tüm verilerine erişim

    Kullanıcı kendisi hakkında toplanan tüm verileri JSON formatında alır
    """
    # Kullanıcı bilgileri
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "subscription_tier": current_user.subscription_tier,
        "created_at": current_user.created_at.isoformat(),
    }

    # Arama geçmişi
    searches = db.query(SearchQuery).filter(
        SearchQuery.user_id == current_user.id
    ).all()

    searches_data = [
        {
            "id": s.id,
            "query_type": s.query_type,
            "created_at": s.created_at.isoformat()
        }
        for s in searches
    ]

    return {
        "user": user_data,
        "searches": searches_data,
        "exported_at": datetime.utcnow().isoformat(),
        "rights": {
            "delete": "/api/v1/gdpr/delete-account",
            "export": "/api/v1/gdpr/my-data"
        }
    }


@router.delete("/delete-account")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    GDPR Madde 17: Unutulma Hakkı (Right to be Forgotten)

    Kullanıcı hesabını ve ilişkili tüm verileri siler
    """
    # İlişkili verileri sil
    db.query(SearchQuery).filter(
        SearchQuery.user_id == current_user.id
    ).delete()

    # Kullanıcıyı sil
    db.delete(current_user)
    db.commit()

    return {
        "message": "Account and all associated data have been permanently deleted",
        "deleted_at": datetime.utcnow().isoformat()
    }


@router.post("/anonymize-visitor/{visitor_id}")
def anonymize_visitor_data(
    visitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ziyaretçi verilerini anonimleştir

    IP adresi ve diğer kişisel veriler anonimleştirilir
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    visitor = db.query(VisitorIdentification).filter(
        VisitorIdentification.id == visitor_id
    ).first()

    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    # IP anonimleştir
    visitor.ip_address = "XXX.XXX.XXX.XXX"
    visitor.user_agent = "[anonymized]"
    visitor.browser_fingerprint = "[anonymized]"

    db.commit()

    return {
        "message": "Visitor data anonymized",
        "visitor_id": visitor_id
    }


@router.get("/data-retention-policy")
def get_retention_policy():
    """
    Veri saklama politikası bilgisi

    KVKK Madde 7: Verilerin saklanma süreleri
    """
    return {
        "policy": {
            "user_data": "Account deletion sonrası hemen silinir",
            "visitor_tracking": "30 gün sonra otomatik anonimleştirme",
            "search_queries": "2 yıl saklama, sonra otomatik silme",
            "email_campaigns": "İstatistik amaçlı 5 yıl saklama",
            "companies": "Süresiz (public business data)"
        },
        "contact": {
            "dpo_email": "privacy@yasin-trade.com",
            "support": "support@yasin-trade.com"
        }
    }
