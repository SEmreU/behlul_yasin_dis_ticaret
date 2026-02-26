"""
Marketplace API Endpoints
TradeKey, ECPlaza, eWorldTrade, IndiaMART, TradeIndia, EC21, Kompass, Thomasnet
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.marketplace_scrapers import MarketplaceScraperService
from app.services.excel_export import ExcelExportService


router = APIRouter(prefix="/marketplace", tags=["marketplace"])


class MarketplaceSearchRequest(BaseModel):
    """Marketplace arama isteği"""
    query: str
    platforms: Optional[List[str]] = None
    country: Optional[str] = None
    search_type: str = "products"  # "products" veya "rfq"
    max_results: int = 20


@router.post("/search-all")
async def search_all_marketplaces(
    request: MarketplaceSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tüm marketplacelerde ara
    
    Desteklenen platformlar:
    - tradekey (RFQ odaklı)
    - ecplaza (Kore)
    - eworldtrade (Global)
    - indiamart (Hindistan)
    - tradeindia (Hindistan ihracatçı)
    - ec21 (7M+ ürün, OEM)
    - kompass (Avrupa)
    - thomasnet (ABD)
    """
    try:
        results = await MarketplaceScraperService.search_all_marketplaces(
            search_query=request.query,
            platforms=request.platforms,
            search_type=request.search_type
        )
        
        total_results = sum(len(v) for v in results.values())
        
        return {
            "success": True,
            "query": request.query,
            "total_platforms": len(results),
            "total_results": total_results,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search-rfqs")
async def search_rfqs(
    request: MarketplaceSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RFQ (Request for Quotation) ara
    
    Özellikle TradeKey, ECPlaza, eWorldTrade'de RFQ taraması yapar
    """
    try:
        # RFQ odaklı platformlar
        rfq_platforms = ['tradekey', 'ecplaza', 'eworldtrade']
        
        if request.platforms:
            rfq_platforms = [p for p in request.platforms if p in rfq_platforms]
        
        results = await MarketplaceScraperService.search_all_marketplaces(
            search_query=request.query,
            platforms=rfq_platforms,
            search_type="rfq"
        )
        
        # RFQ'ları düzleştir
        all_rfqs = []
        for platform, rfqs in results.items():
            all_rfqs.extend(rfqs)
        
        return {
            "success": True,
            "query": request.query,
            "total_rfqs": len(all_rfqs),
            "rfqs": all_rfqs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_marketplace_results(
    query: str = Query(..., description="Arama terimi"),
    platforms: Optional[str] = Query(None, description="Platform listesi (virgülle ayrılmış)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marketplace sonuçlarını Excel olarak indir
    """
    try:
        platform_list = platforms.split(',') if platforms else None
        
        results = await MarketplaceScraperService.search_all_marketplaces(
            search_query=query,
            platforms=platform_list
        )
        
        # Excel'e aktar
        excel_file = ExcelExportService.export_b2b_results(results)
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=marketplace_results_{query}.xlsx"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export-rfqs")
async def export_rfqs(
    query: str = Query(..., description="Arama terimi"),
    country: Optional[str] = Query(None, description="Ülke filtresi"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RFQ listesini Excel olarak indir
    """
    try:
        rfq_platforms = ['tradekey', 'ecplaza', 'eworldtrade']
        
        results = await MarketplaceScraperService.search_all_marketplaces(
            search_query=query,
            platforms=rfq_platforms,
            search_type="rfq"
        )
        
        # RFQ'ları düzleştir
        all_rfqs = []
        for platform, rfqs in results.items():
            all_rfqs.extend(rfqs)
        
        # Ülke filtresi
        if country:
            all_rfqs = [r for r in all_rfqs if country.lower() in r.get('country', '').lower()]
        
        # Excel'e aktar
        excel_file = ExcelExportService.export_marketplace_rfqs(all_rfqs)
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=rfqs_{query}.xlsx"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platforms")
async def list_platforms():
    """
    Desteklenen marketplace platformlarını listele
    """
    return {
        "platforms": [
            {
                "id": "tradekey",
                "name": "TradeKey",
                "url": "https://www.tradekey.com/",
                "type": "RFQ",
                "region": "Global",
                "features": ["RFQ tarama", "Alım talepleri", "Ücretsiz"]
            },
            {
                "id": "ecplaza",
                "name": "ECPlaza",
                "url": "https://www.ecplaza.net/",
                "type": "B2B",
                "region": "Korea/Asia",
                "features": ["Kore pazarı", "Asya tedarikçileri"]
            },
            {
                "id": "eworldtrade",
                "name": "eWorldTrade",
                "url": "https://www.eworldtrade.com/",
                "type": "B2B",
                "region": "Global",
                "features": ["Global ticaret", "RFQ"]
            },
            {
                "id": "indiamart",
                "name": "IndiaMART",
                "url": "https://www.indiamart.com/",
                "type": "B2B",
                "region": "India",
                "features": ["Hindistan'ın en büyüğü", "Makine", "Metal parça"]
            },
            {
                "id": "tradeindia",
                "name": "TradeIndia",
                "url": "https://www.tradeindia.com/",
                "type": "B2B",
                "region": "India",
                "features": ["İhracatçı veritabanı", "Rakip analizi"]
            },
            {
                "id": "ec21",
                "name": "EC21",
                "url": "https://www.ec21.com/",
                "type": "B2B",
                "region": "Global",
                "features": ["7M+ ürün", "OEM arama"]
            },
            {
                "id": "kompass",
                "name": "Kompass",
                "url": "https://www.kompass.com/",
                "type": "Directory",
                "region": "Europe",
                "features": ["Avrupa firmaları", "Yetkili mail"]
            },
            {
                "id": "thomasnet",
                "name": "Thomasnet",
                "url": "https://www.thomasnet.com/",
                "type": "Directory",
                "region": "North America",
                "features": ["ABD/Kanada", "Endüstriyel üretici"]
            }
        ]
    }
