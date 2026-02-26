"""Dashboard Analytics & Reporting Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.company import Company
from app.models.search_query import SearchQuery
from app.models.campaign import EmailCampaign
from app.models.visitor import VisitorIdentification

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ana dashboard istatistikleri

    Returns:
    - Toplam firma sayısı
    - Gönderilen email sayısı
    - Ortalama açılma oranı
    - Kalan kontör
    - Son 7 gün aktivite
    """
    # Toplam firma sayısı
    total_companies = db.query(Company).count()

    # Kullanıcının kampanyaları
    user_campaigns = db.query(EmailCampaign).filter(
        EmailCampaign.user_id == current_user.id
    ).all()

    total_emails_sent = sum(c.sent_count for c in user_campaigns)
    total_emails_opened = sum(c.opened_count for c in user_campaigns)
    avg_open_rate = (total_emails_opened / total_emails_sent * 100) if total_emails_sent > 0 else 0

    # Son 7 günün aramaları
    last_7_days = datetime.utcnow() - timedelta(days=7)
    recent_searches = db.query(SearchQuery).filter(
        SearchQuery.user_id == current_user.id,
        SearchQuery.created_at >= last_7_days
    ).count()

    # Son bulunan firmalar
    recent_companies = db.query(Company).order_by(
        Company.created_at.desc()
    ).limit(5).all()

    # Aktif kampanyalar
    active_campaigns = db.query(EmailCampaign).filter(
        EmailCampaign.user_id == current_user.id,
        EmailCampaign.status.in_(["scheduled", "sending"])
    ).limit(3).all()

    return {
        "stats": {
            "total_companies": total_companies,
            "emails_sent": total_emails_sent,
            "open_rate": round(avg_open_rate, 1),
            "credits_remaining": current_user.query_credits,
            "recent_searches": recent_searches,
        },
        "recent_companies": [
            {
                "id": c.id,
                "name": c.name,
                "country": c.country,
                "source": c.source,
                "created_at": c.created_at.isoformat()
            }
            for c in recent_companies
        ],
        "active_campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "sent_count": c.sent_count,
                "total_recipients": c.total_recipients,
                "status": c.status
            }
            for c in active_campaigns
        ]
    }


@router.get("/export/companies")
def export_companies_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 1000
):
    """
    Firmaları Excel formatında export et

    TODO: pandas + openpyxl ile Excel oluştur
    """
    companies = db.query(Company).limit(limit).all()

    # CSV data
    data = []
    for c in companies:
        data.append({
            "ID": c.id,
            "Name": c.name,
            "Country": c.country,
            "City": c.city,
            "Website": c.website,
            "Email": c.email,
            "Phone": c.phone,
            "Source": c.source,
            "Created": c.created_at.isoformat()
        })

    return {
        "data": data,
        "total": len(data),
        "format": "csv"
    }
