from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.excel_export import ExcelExportService
from app.services.activity_logger import log_activity_safe, Module

router = APIRouter()


class MapsSearchRequest(BaseModel):
    """Harita araştırma request modeli"""
    keywords: str                        # Ana arama terimi
    country: Optional[str] = None
    city: Optional[str] = None
    language: Optional[str] = "en"
    # Legacy alanlar (eski frontend uyumluluğu için)
    keyword1: Optional[str] = None
    keyword2: Optional[str] = None
    keyword3: Optional[str] = None


class MapsSearchResponse(BaseModel):
    """Harita araştırma response modeli"""
    success: bool = True
    results: List[dict]
    total_results: int
    note: Optional[str] = None


@router.post("/search", response_model=MapsSearchResponse)
async def search_maps(
    request: MapsSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Harita tabanlı firma arama.
    3 katmanlı: Google Places API → ScraperAPI Google arama → Mock data
    """
    if current_user.query_credits < 3:
        raise HTTPException(
            status_code=403,
            detail="Yetersiz kredi. Harita araması 3 kredi gerektirir."
        )

    query = request.keywords or request.keyword1 or ""
    country = request.country or ""
    city = request.city or ""

    try:
        current_user.query_credits -= 3
        db.commit()
    except Exception:
        pass

    try:
        from app.services.maps_scraper import GoogleMapsService
        data = await GoogleMapsService.search_companies(query, country, city, max_results=20)
        results = data.get("results", [])
        note = data.get("note")
    except Exception as e:
        results = []
        note = f"Arama hatası: {e}"

    log_activity_safe(
        db, current_user.id,
        module=Module.MAPS,
        action=f"Harita araması: {query[:80]}",
        credits_used=3,
        status="success" if results else "error",
        meta_data={"query": query, "country": country, "city": city, "results_count": len(results)}
    )

    return MapsSearchResponse(
        success=True,
        results=results,
        total_results=len(results),
        note=note,
    )


@router.get("/export")
async def export_map_results(
    keywords: str = "",
    country: str = "",
    city: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Harita sonuçlarını Excel olarak indir"""
    dummy_data = [
        {"Firma Adı": f"{keywords} Import GmbH", "Şehir": city or "Unknown", "Ülke": country or "Unknown",
         "Telefon": "+49 30 1234567", "Website": "www.example.de"},
    ]
    try:
        excel_file = ExcelExportService.export_generic(
            dummy_data, f"maps_{keywords}_{country}"
        )
    except Exception:
        import io, json
        excel_file = io.BytesIO(json.dumps(dummy_data).encode())

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=maps_{keywords}.xlsx"}
    )

