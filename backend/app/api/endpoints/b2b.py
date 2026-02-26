from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.b2b_scraper import B2BScraperService, AlibabaScraper, TradeAtlasScraper, ImportGeniusScraper
from app.services.excel_export import ExcelExportService

router = APIRouter()


class B2BSearchRequest(BaseModel):
    """B2B platform arama isteği"""
    query: str
    max_results: int = 20
    platforms: Optional[List[str]] = None  # ['alibaba', 'tradeatlas', 'importgenius']


@router.post("/search")
async def search_all_platforms(
    request: B2BSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Tüm B2B platformlarda ara
    
    **Platformlar:**
    - Alibaba (ürün araması)
    - TradeAtlas (gümrük verileri)
    - ImportGenius (ABD ithalat verileri)
    
    **Not:**
    - Alibaba: API key gerektirmez (scraping)
    - TradeAtlas: Login gerekebilir
    - ImportGenius: Ücretli API
    """
    try:
        results = await B2BScraperService.search_all_platforms(
            search_query=request.query,
            platforms=request.platforms
        )
        
        total_results = sum(len(v) for v in results.values())
        
        return {
            "query": request.query,
            "total_results": total_results,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alibaba/search")
async def search_alibaba(
    request: B2BSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Alibaba.com'da ürün ara
    
    **Özellikler:**
    - Ürün başlığı
    - Fiyat bilgisi
    - Tedarikçi adı
    - Ürün görseli
    
    **Not:** API key gerektirmez, Playwright ile scraping
    """
    try:
        results = await AlibabaScraper.search_products(
            search_query=request.query,
            max_results=request.max_results
        )
        
        return {
            "query": request.query,
            "platform": "alibaba",
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tradeatlas/search")
async def search_tradeatlas(
    company_name: str,
    country: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    TradeAtlas'ta sevkiyat ara
    
    **Özellikler:**
    - Gümrük verileri
    - Sevkiyat detayları
    - İthalatçı/ihracatçı bilgileri
    
    **Not:** Login gerekebilir veya API subscription
    """
    try:
        results = await TradeAtlasScraper.search_shipments(
            company_name=company_name,
            country=country
        )
        
        return {
            "company": company_name,
            "platform": "tradeatlas",
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/importgenius/search")
async def search_importgenius(
    company_name: str,
    product_keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    ImportGenius'ta ithalat ara
    
    **Özellikler:**
    - ABD ithalat kayıtları
    - Tedarikçi bilgileri
    - Ürün açıklamaları
    - Değer ve miktar
    
    **Not:** Ücretli API subscription gerektirir
    """
    try:
        results = await ImportGeniusScraper.search_imports(
            company_name=company_name,
            product_keyword=product_keyword
        )
        
        return {
            "company": company_name,
            "platform": "importgenius",
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms")
async def list_b2b_platforms():
    """
    Desteklenen B2B platformlarını listele
    
    Returns:
        Platform isimleri, bölgeleri ve özellikleri
    """
    platforms = [
        {
            "name": "Alibaba",
            "region": "China & Global",
            "features": ["Product Search", "Supplier Directory", "Trade Assurance"],
            "active": True,
            "requires_api_key": False,
            "moq": "Medium to High"
        },
        {
            "name": "Made-in-China",
            "region": "China",
            "features": ["Industrial Products", "Verified Suppliers", "Factory Audits"],
            "active": True,
            "requires_api_key": False,
            "moq": "Medium"
        },
        {
            "name": "DHgate",
            "region": "China",
            "features": ["Low MOQ", "Dropshipping", "Escrow Payment"],
            "active": True,
            "requires_api_key": False,
            "moq": "Low"
        },
        {
            "name": "Global Sources",
            "region": "Hong Kong & China",
            "features": ["Premium Quality", "Verified Suppliers", "Trade Shows"],
            "active": True,
            "requires_api_key": False,
            "moq": "High"
        },
        {
            "name": "Yiwugo",
            "region": "China (Yiwu Market)",
            "features": ["Small Commodities", "Ultra-Low Prices", "Huge Variety"],
            "active": True,
            "requires_api_key": False,
            "moq": "Low"
        },
        {
            "name": "TradeAtlas",
            "region": "Global",
            "features": ["Customs Data", "Shipment Tracking"],
            "active": True,
            "requires_api_key": True,
            "moq": "N/A"
        },
        {
            "name": "ImportGenius",
            "region": "USA",
            "features": ["Import Records", "Buyer-Supplier Matching"],
            "active": True,
            "requires_api_key": True,
            "moq": "N/A"
        }
    ]
    
    return {"platforms": platforms}


@router.post("/made-in-china/search")
async def search_made_in_china(
    request: B2BSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Made-in-China.com'da ürün ara
    
    **Özellikler:**
    - Endüstriyel ürünler
    - Doğrulanmış tedarikçiler
    - Fabrika denetimleri
    """
    try:
        from app.services.b2b_scraper import MadeInChinaScraper
        
        results = await MadeInChinaScraper.search_products(
            search_query=request.query,
            max_results=request.max_results
        )
        
        return {
            "query": request.query,
            "platform": "made-in-china",
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dhgate/search")
async def search_dhgate(
    request: B2BSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    DHgate.com'da ürün ara
    
    **Özellikler:**
    - Düşük MOQ
    - Dropshipping için ideal
    - Escrow ödeme
    """
    try:
        from app.services.b2b_scraper import DHgateScraper
        
        results = await DHgateScraper.search_products(
            search_query=request.query,
            max_results=request.max_results
        )
        
        return {
            "query": request.query,
            "platform": "dhgate",
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
