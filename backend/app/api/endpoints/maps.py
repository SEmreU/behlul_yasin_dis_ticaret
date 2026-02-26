from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.excel_export import ExcelExportService

router = APIRouter()


class MapsSearchRequest(BaseModel):
    """Harita araştırma request modeli"""
    country: str
    language: str
    keyword1: str
    keyword2: Optional[str] = None
    keyword3: Optional[str] = None
    city: Optional[str] = None


class MapsSearchResponse(BaseModel):
    """Harita araştırma response modeli"""
    results: List[dict]
    total: int
    search_params: dict


@router.post("/search", response_model=MapsSearchResponse)
async def search_maps(
    request: MapsSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Harita tabanlı firma arama
    
    **Özellikler:**
    - Google Maps API entegrasyonu
    - Yerel alan araması
    - Firma iletişim bilgileri çıkarma
    - Excel export desteği
    
    **Credit:** 3 credits per search
    """
    # Kontör kontrolü
    if current_user.query_credits < 3:
        raise HTTPException(
            status_code=403,
            detail="Yetersiz kredi. Harita araması 3 kredi gerektirir."
        )
    
    # TODO: Implement actual Google Maps API search
    # 1. Build search query from keywords
    # 2. Search specific country/city
    # 3. Extract business details (name, address, phone, website)
    # 4. Geocode locations
    # 5. Save to database
    
    # Kontör düş
    current_user.query_credits -= 3
    db.commit()
    
    # Dummy response
    results = [
        {
            "id": 1,
            "name": "Sample Company GmbH",
            "address": "123 Business St, " + request.city if request.city else "Unknown",
            "city": request.city or "Unknown",
            "country": request.country,
            "phone": "+49 123 456789",
            "website": "www.example.com",
            "location": {"lat": 52.520008, "lng": 13.404954}
        }
    ]
    
    return {
        "results": results,
        "total": len(results),
        "search_params": {
            "country": request.country,
            "keywords": [request.keyword1, request.keyword2, request.keyword3],
            "city": request.city
        }
    }


@router.get("/export")
async def export_map_results(
    country: str,
    keywords: str,  # comma-separated
    city: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Harita arama sonuçlarını Excel olarak indir
    
    Args:
        country: Ülke
        keywords: Anahtar kelimeler (virgülle ayrılmış)
        city: Şehir (opsiyonel)
        
    Returns:
        Excel file with company data
    """
    # TODO: Get actual search results from database or re-run search
    # For now, using dummy data
    companies = [
        {
            "name": "Sample Company GmbH",
            "address": f"123 Business St, {city}" if city else "Unknown",
            "phone": "+49 123 456789",
            "email": "info@example.com",
            "website": "www.example.com",
            "category": keywords.split(',')[0],
            "rating": "4.5",
            "latitude": 52.520008,
            "longitude": 13.404954
        }
    ]
    
    # Excel'e aktar
    excel_file = ExcelExportService.export_map_results(companies)
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=map_results_{country}.xlsx"}
    )
