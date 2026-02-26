from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.core.deps import get_db, get_current_active_user
from app.services.maps_scraper import GoogleMapsScraper
from app.models.user import User

router = APIRouter()


class ScrapingRequest(BaseModel):
    keyword: str
    location: str
    max_results: int = 100


@router.post("/google-maps")
async def scrape_google_maps(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Google Maps'ten firma toplama

    **Kullanım:**
    - keyword: "automotive parts", "piston manufacturer" vb.
    - location: "Germany", "Stuttgart, Germany", "Berlin" vb.
    - max_results: Maksimum firma sayısı (default: 100)

    **Arka Planda Çalışır:**
    Scraping işlemi uzun sürebilir, arka planda çalışır.
    Sonuçlar companies tablosuna kaydedilir.

    **Kontör:** 5 credit (ağır işlem)
    """
    if current_user.query_credits < 5:
        return {"error": "Insufficient credits. Scraping requires 5 credits."}

    # Kontör düş
    current_user.query_credits -= 5
    db.commit()

    # Background task olarak çalıştır
    background_tasks.add_task(
        GoogleMapsScraper.scrape_companies,
        keyword=request.keyword,
        location=request.location,
        max_results=request.max_results,
        db=db
    )

    return {
        "status": "started",
        "message": "Scraping started in background. Results will be saved to database.",
        "keyword": request.keyword,
        "location": request.location
    }


@router.get("/status/{job_id}")
async def get_scraping_status(job_id: str):
    """
    Scraping job durumu

    TODO: Celery veya Redis ile job tracking implementasyonu
    """
    return {
        "job_id": job_id,
        "status": "processing",
        "progress": 45,
        "companies_found": 23
    }
