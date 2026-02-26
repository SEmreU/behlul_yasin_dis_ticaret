from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User

router = APIRouter()


class FairAnalysisRequest(BaseModel):
    """Fair analysis request model"""
    exhibitor_urls: Optional[List[str]] = None
    product_keywords: List[str]
    gtip_code: Optional[str] = None
    sector_keywords: Optional[List[str]] = None


class FairAnalysisResponse(BaseModel):
    """Fair analysis response model"""
    matching_companies: List[dict]
    total_analyzed: int
    match_rate: float


@router.post("/analyze", response_model=FairAnalysisResponse)
async def analyze_fair_exhibitors(
    request: FairAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fuar katılımcı listesini analiz et ve eşleşen firmaları bul
    
    **Kullanım Senaryosu:**
    Automechanika gibi büyük fuarlara katılmadan önce,
    sadece sizinle alakalı firmaları tespit edin.
    
    **Analiz:**
    - Web sitelerini scrape et
    - Ürün kataloglarını incele
    - GTİP kodlarıyla eşleştir
    - Sektör benzerliği skorla
    
    **Credit:** 2 credits per company analyzed
    """
    company_count = len(request.exhibitor_urls) if request.exhibitor_urls else 0
    credits_needed = company_count * 2
    
    if current_user.query_credits < credits_needed:
        raise HTTPException(
            status_code=403,
            detail=f"Yetersiz kredi. {company_count} firma analizi {credits_needed} kredi gerektirir."
        )
    
    # TODO: Implement fair analysis logic
    # 1. For each exhibitor URL:
    #    - Scrape company website
    #    - Extract product information
    #    - Match with GTIP codes
    #    - Calculate similarity score
    # 2. Filter companies above threshold
    # 3. Rank by relevance
    # 4. Save analysis results
    
    # Kontör düş
    if company_count > 0:
        current_user.query_credits -= credits_needed
        db.commit()
    
    # Dummy response
    matching_companies = [
        {
            "company_name": "Sample Parts GmbH",
            "country": "Germany",
            "website": "www.sampleparts.de",
            "products": ["Engine Parts", "Pistons", "Cylinders"],
            "match_score": 0.87,
            "gtip_match": True,
            "reason": "Piston üreticisi - doğrudan müşteri potansiyeli"
        }
    ]
    
    return {
        "matching_companies": matching_companies,
        "total_analyzed": company_count,
        "match_rate": len(matching_companies) / company_count if company_count > 0 else 0
    }


@router.post("/upload-exhibitor-list")
async def upload_exhibitor_list(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fuar katılımcı listesini Excel/PDF olarak yükle
    
    **Desteklenen Formatlar:**
    - Excel (.xlsx, .xls)
    - PDF (metin çıkarma ile)
    
    Returns:
        Yükleme başarılı, analiz job ID
    """
    # TODO: Implement file upload and parsing
    # 1. Save uploaded file
    # 2. Parse Excel/PDF
    # 3. Extract company names and URLs
    # 4. Queue analysis job
    # 5. Return job ID
    
    return {
        "message": "Fuar listesi yükleme özelliği yakında eklenecek",
        "filename": file.filename,
        "status": "pending"
    }


@router.get("/results/{analysis_id}")
async def get_analysis_results(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fuar analiz sonuçlarını getir
    
    Args:
        analysis_id: Saved analysis ID
        
    Returns:
        Matching companies with scores and details
    """
    # TODO: Get analysis results from database
    
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "results": []
    }


@router.get("/export/{analysis_id}")
async def export_fair_results(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fuar analiz sonuçlarını Excel olarak indir
    
    **Excel İçeriği:**
    - Firma adı
    - Ülke
    - Web sitesi
    - Ürünler
    - Eşleşme skoru
    - İletişim bilgileri
    """
    # TODO: Generate Excel export
    
    return {
        "message": "Excel export özelliği yakında eklenecek",
        "analysis_id": analysis_id
    }
