from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.core.deps import get_db, get_current_active_user
from app.services.email_automation import EmailAutomationService
from app.models.user import User
from app.models.campaign import EmailCampaign

router = APIRouter()


class CampaignCreateRequest(BaseModel):
    name: str
    subject: str
    body_template: str
    target_company_ids: List[int]
    attachments: Optional[List[dict]] = None


class CampaignResponse(BaseModel):
    id: int
    name: str
    status: str
    total_recipients: int
    sent_count: int
    opened_count: int
    clicked_count: int

    class Config:
        from_attributes = True


@router.post("/create", response_model=CampaignResponse)
def create_campaign(
    request: CampaignCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Yeni email kampanyası oluştur

    **Body Template Placeholders:**
    - {company_name}: Firma adı
    - {country}: Ülke
    - {contact_name}: İletişim kişisi
    - {product}: Ürün bilgisi

    **Örnek:**
    ```
    Sayın {company_name} Yetkilisi,

    {country} pazarında faaliyet gösteren firmanızla
    iş birliği yapmak isteriz...
    ```
    """
    campaign = EmailAutomationService.create_campaign(
        db=db,
        user_id=current_user.id,
        name=request.name,
        subject=request.subject,
        body_template=request.body_template,
        target_company_ids=request.target_company_ids,
        attachments=request.attachments
    )

    return campaign


@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Kampanyayı gönder

    **AI Kişiselleştirme:**
    Her email otomatik olarak AI ile kişiselleştirilir.

    **Tracking:**
    - Pixel tracking ile açılma
    - Link tracking ile tıklama
    """
    # Kampanya sahipliği kontrolü
    campaign = db.query(EmailCampaign).filter(
        EmailCampaign.id == campaign_id,
        EmailCampaign.user_id == current_user.id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = await EmailAutomationService.send_campaign(db, campaign_id)

    return result


@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 50
):
    """Kullanıcının kampanyalarını listele"""
    campaigns = db.query(EmailCampaign).filter(
        EmailCampaign.user_id == current_user.id
    ).order_by(EmailCampaign.created_at.desc()).limit(limit).all()

    return campaigns


@router.get("/{campaign_id}/stats")
def get_campaign_stats(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Kampanya detaylı istatistikleri"""
    campaign = db.query(EmailCampaign).filter(
        EmailCampaign.id == campaign_id,
        EmailCampaign.user_id == current_user.id
    ).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    open_rate = (campaign.opened_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0
    click_rate = (campaign.clicked_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0

    return {
        "id": campaign.id,
        "name": campaign.name,
        "status": campaign.status,
        "total_recipients": campaign.total_recipients,
        "sent_count": campaign.sent_count,
        "opened_count": campaign.opened_count,
        "clicked_count": campaign.clicked_count,
        "bounced_count": campaign.bounced_count,
        "open_rate": round(open_rate, 2),
        "click_rate": round(click_rate, 2),
        "created_at": campaign.created_at.isoformat(),
        "started_at": campaign.started_at.isoformat() if campaign.started_at else None,
        "completed_at": campaign.completed_at.isoformat() if campaign.completed_at else None,
    }
