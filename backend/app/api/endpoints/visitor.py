from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.visitor_tracking import VisitorTrackingService
from app.services.excel_export import ExcelExportService
from app.models.visitor import VisitorIdentification

router = APIRouter()


class VisitorTrackRequest(BaseModel):
    session_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_permission_granted: bool = False


class VisitorTrackResponse(BaseModel):
    visitor_id: int
    identified_company: Optional[dict] = None
    confidence_score: float
    location_source: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/track", response_model=VisitorTrackResponse)
async def track_visitor(
    data: VisitorTrackRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Ziyaretçi tracking endpoint — web sitenize yerleştirilecek JS bu endpoint'i çağırır.
    Auth gerektirmez (public endpoint), ziyaretçi bilgilerini DB'ye kaydeder.
    """
    ip_address = request.client.host
    if "x-forwarded-for" in request.headers:
        ip_address = request.headers["x-forwarded-for"].split(",")[0].strip()

    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer")

    visitor = await VisitorTrackingService.track_visitor(
        db=db,
        session_id=data.session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referer=referer,
        latitude=data.latitude,
        longitude=data.longitude,
        location_permission_granted=data.location_permission_granted
    )

    response_data = {
        "visitor_id": visitor.id,
        "identified_company": None,
        "confidence_score": visitor.confidence_score or 0.0,
        "location_source": visitor.location_source
    }

    if visitor.identified_company_id and visitor.identified_company:
        response_data["identified_company"] = {
            "id": visitor.identified_company.id,
            "name": visitor.identified_company.name,
            "country": visitor.identified_company.country,
            "website": visitor.identified_company.website,
        }

    return response_data


def _visitor_to_dict(v: VisitorIdentification) -> dict:
    """
    Frontend'in beklediği formata dönüştür:
    - ip: IP adresi
    - company: Firma adı (identified_company veya ISP org)
    - email: ISP org'dan tahmin edilen domain email
    - confidence_score: 0-1 arası
    """
    ip = v.ip_address or ""

    # Firma adı: önce eşleşen company, yoksa ISP org'u parse et
    company = ""
    if v.identified_company:
        company = v.identified_company.name
    elif hasattr(v, "org") and v.org:
        # org genelde "AS12345 Company Name" formatında gelir
        parts = (v.org or "").split(" ", 1)
        company = parts[1] if len(parts) > 1 else v.org

    # Email tahmini: domain'den info@domain.com üret
    email = ""
    if v.identified_company and getattr(v.identified_company, "website", None):
        site = v.identified_company.website or ""
        site = site.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        if site:
            email = f"info@{site}"

    return {
        "id": v.id,
        "company": company or "Bilinmiyor",
        "country": v.country or "",
        "city": v.city or "",
        "ip": ip,
        "email": email,
        "created_at": v.created_at.isoformat() if v.created_at else "",
        "confidence_score": v.confidence_score or 0.0,
        "location_source": v.location_source or "ip_geolocation",
    }


@router.get("/visitors", response_model=list)
async def list_visitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 100,
    skip: int = 0
):
    """Son ziyaretçileri listele (auth gerekli)"""
    visitors = db.query(VisitorIdentification).order_by(
        VisitorIdentification.created_at.desc()
    ).offset(skip).limit(limit).all()

    return [_visitor_to_dict(v) for v in visitors]


@router.get("/export")
async def export_visitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 1000
):
    """Ziyaretçi listesini Excel olarak indir (auth gerekli)"""
    visitors = db.query(VisitorIdentification).order_by(
        VisitorIdentification.created_at.desc()
    ).limit(limit).all()

    visitor_data = [
        {
            "Zaman": v.created_at.isoformat() if v.created_at else "",
            "Firma": v.identified_company.name if v.identified_company else "Bilinmiyor",
            "Ülke": v.country or "",
            "Şehir": v.city or "",
            "IP Adresi": v.ip_address or "",
            "Sayfa / Referer": v.referer or "Direkt",
            "Güven Skoru": f"{(v.confidence_score or 0)*100:.0f}%",
        }
        for v in visitors
    ]

    excel_file = ExcelExportService.export_visitors(visitor_data)

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=visitors.xlsx"}
    )

