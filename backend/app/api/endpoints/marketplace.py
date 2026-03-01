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
from app.core.deps import get_current_active_user as get_current_user
from app.models.user import User
from app.services.marketplace_scrapers import MarketplaceScraperService
from app.services.excel_export import ExcelExportService


router = APIRouter(tags=["marketplace"])


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
        import logging
        logging.getLogger("marketplace").warning("Marketplace search error: %s", str(e)[:200])
        return {
            "success": False,
            "query": request.query,
            "total_platforms": 0,
            "total_results": 0,
            "results": {},
            "error": "Arama sırasında hata oluştu, lütfen tekrar deneyin."
        }


@router.post("/search-rfqs")
async def search_rfqs(
    request: MarketplaceSearchRequest,
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
        import logging
        logging.getLogger("marketplace").warning("RFQ search error: %s", str(e)[:200])
        return {
            "success": False,
            "query": request.query,
            "total_rfqs": 0,
            "rfqs": [],
            "error": "RFQ araması sırasında hata oluştu."
        }


@router.get("/export")
async def export_marketplace_results(
    query: str = Query(..., description="Arama terimi"),
    platforms: Optional[str] = Query(None, description="Platform listesi (virgülle ayrılmış)"),
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
        import logging
        logging.getLogger("marketplace").warning("Export error: %s", str(e)[:200])
        return {"error": "Export sırasında hata oluştu.", "detail": str(e)[:200]}


@router.get("/export-rfqs")
async def export_rfqs(
    query: str = Query(..., description="Arama terimi"),
    country: Optional[str] = Query(None, description="Ülke filtresi"),
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
        import logging
        logging.getLogger("marketplace").warning("RFQ export error: %s", str(e)[:200])
        return {"error": "RFQ export sırasında hata oluştu.", "detail": str(e)[:200]}


class USASearchRequest(BaseModel):
    query: str
    state: Optional[str] = None           # Eyalet filtresi
    company_type: Optional[str] = None    # importer, distributor, oem, retailer
    hs_code: Optional[str] = None
    max_results: int = 20


class ChinaSearchRequest(BaseModel):
    query: str
    query_chinese: Optional[str] = None   # Çince arama terimi
    min_order: Optional[str] = None
    certificate: Optional[str] = None     # ISO 9001, CE, SGS
    max_results: int = 20


@router.post("/search-usa")
async def search_usa_market(
    request: USASearchRequest,
):
    """
    ABD Pazarı Özel Arama

    Kaynaklar:
    - **Thomasnet**: ABD/Kanada endüstriyel üreticiler
    - **ImportGenius**: ABD ithalat beyan kayıtları (kısıtlı)
    - **Panjiva/S&P Global**: Gümrük beyanı veritabanı (link)
    - **USASpending.gov**: Federal tedarik kayıtları
    - **Kompass USA**: Kuzey Amerika firma rehberi
    """
    try:
        from app.services.b2b_scraper import get_api_key
        import httpx, urllib.parse

        api_key = get_api_key()
        query = request.query
        results_by_source: dict = {}

        # --- 1. Thomasnet ---
        thomasnet_url = f"https://www.thomasnet.com/search/?what={urllib.parse.quote(query)}&where={urllib.parse.quote(request.state or 'United+States')}"
        if api_key:
            scraper_url = f"https://api.scraperapi.com/?api_key={api_key}&url={urllib.parse.quote(thomasnet_url)}&render=true"
            try:
                async with httpx.AsyncClient(timeout=25) as client:
                    resp = await client.get(scraper_url)
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, "html.parser")
                    items = []
                    # Thomasnet result cards
                    for card in soup.select(".profile-card, .supplier-profile-card, [class*='CompanyCard']")[:request.max_results]:
                        name_el = card.select_one("h2, h3, [class*='name'], [class*='company']")
                        loc_el = card.select_one("[class*='location'], [class*='city']")
                        link_el = card.select_one("a[href]")
                        if name_el:
                            href = link_el["href"] if link_el else ""
                            if href and not href.startswith("http"):
                                href = "https://www.thomasnet.com" + href
                            items.append({
                                "source": "Thomasnet",
                                "title": name_el.get_text(strip=True),
                                "company": name_el.get_text(strip=True),
                                "location": loc_el.get_text(strip=True) if loc_el else (request.state or "USA"),
                                "country": "ABD",
                                "url": href or thomasnet_url,
                                "type": request.company_type or "Manufacturer/Supplier",
                            })
                    results_by_source["thomasnet"] = items
            except Exception as e:
                print(f"[Thomasnet scrape] {e}")

        if not results_by_source.get("thomasnet"):
            results_by_source["thomasnet"] = [
                {
                    "source": "Thomasnet",
                    "title": f'"{query}" — Thomasnet ABD Üretici Arama',
                    "company": "Thomasnet.com",
                    "location": request.state or "USA",
                    "country": "ABD",
                    "url": thomasnet_url,
                    "type": "Link (ScraperAPI key ekleyin → gerçek sonuçlar)",
                }
            ]

        # --- 2. ImportGenius / Panjiva (public link) ---
        import_genius_url = f"https://www.importgenius.com/search?q={urllib.parse.quote(query)}&country=us"
        panjiva_url = f"https://panjiva.com/search?q={urllib.parse.quote(query)}&country[]=US"
        results_by_source["import_records"] = [
            {
                "source": "ImportGenius",
                "title": f'"{query}" ABD İthalat Kayıtları',
                "company": "ImportGenius.com",
                "location": "USA",
                "country": "ABD",
                "url": import_genius_url,
                "type": "Gümrük Beyanı Veritabanı",
            },
            {
                "source": "Panjiva (S&P Global)",
                "title": f'"{query}" Panjiva Tedarik Zinciri',
                "company": "Panjiva.com",
                "location": "USA",
                "country": "ABD",
                "url": panjiva_url,
                "type": "Gümrük Beyanı Veritabanı",
            },
        ]

        # --- 3. Kompass USA ---
        kompass_url = f"https://us.kompass.com/search/?text={urllib.parse.quote(query)}"
        results_by_source["kompass_usa"] = [
            {
                "source": "Kompass USA",
                "title": f'"{query}" — Kompass Kuzey Amerika',
                "company": "Kompass.com",
                "location": "North America",
                "country": "ABD/Kanada",
                "url": kompass_url,
                "type": "Firma Rehberi",
            }
        ]

        # --- 4. HS kodu varsa Datamyne/USITC ---
        if request.hs_code:
            hs = request.hs_code.replace(".", "")
            usitc_url = f"https://dataweb.usitc.gov/trade/annual/HTSAnnotated?column=imports&HTS={hs}"
            results_by_source["usitc"] = [
                {
                    "source": "USITC Dataweb",
                    "title": f"HS {request.hs_code} ABD İthalat İstatistik",
                    "company": "dataweb.usitc.gov",
                    "location": "USA",
                    "country": "ABD",
                    "url": usitc_url,
                    "type": "Resmi İthalat Verisi",
                }
            ]

        total = sum(len(v) for v in results_by_source.values())
        return {
            "success": True,
            "query": query,
            "market": "usa",
            "total_results": total,
            "results": results_by_source,
            "note": "ScraperAPI key ekleyin → Thomasnet gerçek firma listesi alınır",
        }

    except Exception as e:
        import logging
        logging.getLogger("marketplace").warning("USA market search error: %s", str(e)[:200])
        return {
            "success": False,
            "query": request.query,
            "market": "usa",
            "total_results": 0,
            "results": {},
            "error": "ABD pazarı araması sırasında hata oluştu."
        }


@router.post("/search-china")
async def search_china_market(
    request: ChinaSearchRequest,
):
    """
    Çin Pazarı Özel Arama

    Kaynaklar:
    - **Alibaba.com**: En büyük B2B platform
    - **Made-in-China.com**: Çinli üreticiler
    - **DHgate**: Düşük MOQ dropshipping
    - **1688.com**: Çin iç pazarı, toptan fiyat
    - **Global Sources**: Doğrulanmış Çin tedarikçileri
    """
    from app.services.b2b_scraper import (
        AlibabaScraper,
        MadeInChinaScraper,
        DHgateScraper,
    )
    import asyncio

    search_q = request.query_chinese or request.query

    try:
        tasks = [
            AlibabaScraper.search_products(request.query, request.max_results),
            MadeInChinaScraper.search_products(request.query, request.max_results),
            DHgateScraper.search_products(request.query, request.max_results),
        ]
        alibaba_r, mic_r, dhgate_r = await asyncio.gather(*tasks, return_exceptions=True)

        results_by_source = {
            "alibaba": alibaba_r if isinstance(alibaba_r, list) else [],
            "made_in_china": mic_r if isinstance(mic_r, list) else [],
            "dhgate": dhgate_r if isinstance(dhgate_r, list) else [],
        }

        import urllib.parse
        # 1688 (iç pazar, link only)
        link_1688 = f"https://s.1688.com/selloffer/offer_search.htm?keywords={urllib.parse.quote(search_q)}"
        # Sertifika filtresi — Alibaba Advanced Search
        cert_filter = ""
        if request.certificate and request.certificate != "Hepsi":
            cert_map = {"ISO 9001": "ISOCertified", "CE": "CECertified", "SGS Denetimli": "SGSAudit"}
            cert_filter = cert_map.get(request.certificate, "")

        results_by_source["1688"] = [
            {
                "source": "1688.com",
                "title": f'"{search_q}" — 1688 Çin İç Pazar Toptan Arama',
                "company": "1688.com (Alibaba Group)",
                "country": "Çin",
                "url": link_1688,
                "type": "Çin İç Pazar (Toptan)",
                "note": "1688 kayıt/Çince hesap gerektirir",
            }
        ]

        gs_url = f"https://www.globalsources.com/searchproduct.aspx?Q={urllib.parse.quote(request.query)}"
        results_by_source["global_sources"] = [
            {
                "source": "Global Sources",
                "title": f'"{request.query}" — Global Sources Doğrulanmış Tedarikçi',
                "company": "globalsources.com",
                "country": "Çin",
                "url": gs_url,
                "type": "Doğrulanmış Çin Tedarikçisi",
            }
        ]

        total = sum(len(v) for v in results_by_source.values())
        return {
            "success": True,
            "query": request.query,
            "market": "china",
            "total_results": total,
            "results": results_by_source,
        }

    except Exception as e:
        import logging
        logging.getLogger("marketplace").warning("China market search error: %s", str(e)[:200])
        return {
            "success": False,
            "query": request.query,
            "market": "china",
            "total_results": 0,
            "results": {},
            "error": "Çin pazarı araması sırasında hata oluştu."
        }


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
