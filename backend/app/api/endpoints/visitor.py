from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.core.deps import get_db
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
    Ziyaretçi tracking endpoint

    Web sitenize yerleştirilecek JavaScript bu endpoint'i çağırır.

    **Request Body:**
    - session_id: Unique session identifier
    - latitude: GPS enlem (opsiyonel, izin gerekli)
    - longitude: GPS boylam (opsiyonel, izin gerekli)
    - location_permission_granted: GPS izni verildi mi?

    **Response:**
    - visitor_id: Tracking ID
    - identified_company: Eşleşen firma bilgileri
    - confidence_score: Eşleşme güven skoru (0-1)
    """
    # Client IP al
    ip_address = request.client.host
    if "x-forwarded-for" in request.headers:
        ip_address = request.headers["x-forwarded-for"].split(",")[0].strip()

    # User agent
    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer")

    # Visitor tracking
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

    # Response hazırla
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


@router.get("/visitors", response_model=list)
async def list_visitors(
    db: Session = Depends(get_db),
    limit: int = 100,
    skip: int = 0
):
    """
    Son ziyaretçileri listele (Admin için)

    Query params:
    - limit: Maksimum sonuç sayısı (default: 100)
    - skip: Atlanacak kayıt sayısı (pagination)
    """
    visitors = db.query(VisitorIdentification).order_by(
        VisitorIdentification.created_at.desc()
    ).offset(skip).limit(limit).all()

    return [
        {
            "id": v.id,
            "session_id": v.session_id,
            "ip_address": v.ip_address,
            "country": v.country,
            "city": v.city,
            "identified_company": {
                "id": v.identified_company.id,
                "name": v.identified_company.name,
            } if v.identified_company else None,
            "confidence_score": v.confidence_score,
            "created_at": v.created_at.isoformat(),
        }
        for v in visitors
    ]


@router.get("/export")
async def export_visitors(
    db: Session = Depends(get_db),
    limit: int = 1000
):
    """
    Ziyaretçi listesini Excel olarak indir
    
    Query params:
    - limit: Maksimum kayıt sayısı (default: 1000)
    """
    visitors = db.query(VisitorIdentification).order_by(
        VisitorIdentification.created_at.desc()
    ).limit(limit).all()
    
    # Dict formatına çevir
    visitor_data = [
        {
            "created_at": v.created_at,
            "company_name": v.identified_company.name if v.identified_company else "Unknown",
            "country": v.country or "Unknown",
            "city": v.city or "Unknown",
            "ip_address": v.ip_address,
            "page_url": v.referer or "Direct",
            "referrer": v.referer,
            "user_agent": v.user_agent
        }
        for v in visitors
    ]
    
    # Excel'e aktar
    excel_file = ExcelExportService.export_visitors(visitor_data)
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=visitors.xlsx"}
    )
