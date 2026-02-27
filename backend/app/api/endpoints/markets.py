"""
Pazar Arama Endpoint'leri
- /china/search  → 5 Çin platformu (b2b_scraper.py)
- /usa/search    → Thomasnet + gümrük veri fallback'leri
- /trade-data    → UN Comtrade ücretsiz API
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User

router = APIRouter()


# ─── Request / Response Models ────────────────────────────────────────────────

class ChinaSearchRequest(BaseModel):
    product: str
    market: str = "china"
    product_cn: Optional[str] = None
    min_order_qty: Optional[str] = None
    certificate: Optional[str] = None
    filters: Optional[dict] = None


class USASearchRequest(BaseModel):
    product: str
    market: str = "usa"
    state: Optional[str] = None
    company_type: Optional[str] = None
    hs_code: Optional[str] = None
    filters: Optional[dict] = None


class MarketSearchResponse(BaseModel):
    results: list
    total: int
    market: str
    sources_used: list
    note: Optional[str] = None


# ─── UN Comtrade (ücretsiz resmi API) ────────────────────────────────────────

async def _fetch_un_comtrade(hs_code: str, reporter: str = "all", partner: str = "all") -> List[dict]:
    """UN Comtrade ücretsiz API — resmi ticaret istatistikleri"""
    import httpx, os

    api_key = os.getenv("UN_COMTRADE_API_KEY", "")
    base = "https://comtradeapi.un.org/data/v1/getTariffline/C/A"
    if not hs_code:
        return []

    params = {
        "reporterCode": reporter,
        "partnerCode": partner,
        "cmdCode": hs_code[:6],
        "flowCode": "M",
        "period": "2023",
        "maxRecords": "20",
    }
    if api_key:
        params["subscription-key"] = api_key

    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(base, params=params)
            data = r.json()
            records = data.get("data", [])[:20]
            return [
                {
                    "reporter": rec.get("reporterDesc", ""),
                    "partner": rec.get("partnerDesc", ""),
                    "trade_value_usd": rec.get("primaryValue", 0),
                    "quantity": rec.get("qty", 0),
                    "hs_code": rec.get("cmdCode", hs_code),
                    "source": "un_comtrade",
                    "url": f"https://comtrade.un.org/data/?hs={hs_code}",
                }
                for rec in records
            ]
    except Exception as e:
        print(f"[UN Comtrade] {e}")
        return []


# ─── China Market Search ──────────────────────────────────────────────────────

@router.post("/china/search", response_model=MarketSearchResponse)
async def search_china_market(
    request: ChinaSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Çin pazarı — 5 platform paralel tarama
    Alibaba · Made-in-China · DHgate · 1688 · Global Sources
    ScraperAPI key varsa gerçek ürün/fiyat/tedarikçi verisi döner.
    Credit: 3
    """
    if current_user.query_credits < 3:
        raise HTTPException(status_code=403, detail="Yetersiz kredi. Çin pazarı 3 kredi gerektirir.")

    current_user.query_credits -= 3
    db.commit()

    from app.services.b2b_scraper import (
        AlibabaScraper,
        MadeInChinaScraper,
        DHgateScraper,
        Scraper1688,
        GlobalSourcesScraper,
    )

    query = request.product
    if request.product_cn:
        # 1688 için Çince isim öncelikli
        query_cn = request.product_cn
    else:
        query_cn = query

    try:
        results_list = await asyncio.gather(
            AlibabaScraper.search_products(query, max_results=10),
            MadeInChinaScraper.search_products(query, max_results=8),
            DHgateScraper.search_products(query, max_results=8),
            Scraper1688.search_products(query_cn, max_results=8),
            GlobalSourcesScraper.search_products(query, max_results=6),
            return_exceptions=True,
        )
    except Exception as e:
        results_list = [[] for _ in range(5)]

    all_results = []
    sources = []
    source_names = ["alibaba", "made-in-china", "dhgate", "1688", "global-sources"]

    for i, res in enumerate(results_list):
        if isinstance(res, list) and res:
            all_results.extend(res)
            sources.append(source_names[i])

    # Sertifika filtresi
    if request.certificate and request.certificate != "Hepsi":
        all_results = [
            r for r in all_results
            if request.certificate.lower() in str(r).lower()
        ] or all_results  # filtre sonuç yoksa hepsini göster

    note = None
    if not sources:
        note = "ScraperAPI key ekleyin → Gerçek Çin tedarikçi verisi için (Ayarlar → Scraping & Proxy)"

    return MarketSearchResponse(
        results=all_results,
        total=len(all_results),
        market="china",
        sources_used=sources or source_names,
        note=note,
    )


# ─── USA Market Search ────────────────────────────────────────────────────────

@router.post("/usa/search", response_model=MarketSearchResponse)
async def search_usa_market(
    request: USASearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    ABD pazarı — Thomasnet + gümrük veri kaynakları
    Thomasnet (ScraperAPI ile gerçek) + UN Comtrade + ücretli fallback linkleri
    Credit: 4
    """
    if current_user.query_credits < 4:
        raise HTTPException(status_code=403, detail="Yetersiz kredi. ABD pazarı 4 kredi gerektirir.")

    current_user.query_credits -= 4
    db.commit()

    from app.services.b2b_scraper import ThomasnetScraper

    all_results = []
    sources_used = []

    # 1. Thomasnet (mevcut scraper)
    try:
        thomasnet_results = await ThomasnetScraper.search_products(request.product, max_results=15)
        if thomasnet_results:
            # Eyalet filtresi
            if request.state and request.state != "Tüm ABD":
                thomasnet_results = [
                    r for r in thomasnet_results
                    if request.state.lower() in str(r.get("address", "")).lower()
                ] or thomasnet_results
            all_results.extend(thomasnet_results)
            sources_used.append("thomasnet")
    except Exception as e:
        print(f"[USA/Thomasnet] {e}")

    # 2. UN Comtrade (ücretsiz resmi istatistik)
    if request.hs_code:
        try:
            comtrade_data = await _fetch_un_comtrade(request.hs_code, reporter="842")  # 842 = USA
            if comtrade_data:
                all_results.extend(comtrade_data)
                sources_used.append("un_comtrade")
        except Exception as e:
            print(f"[USA/Comtrade] {e}")

    # 3. Ücretli kaynak linkleri (key varsa ilerleyen versiyonda kullanılacak)
    import os
    paid_links = []
    if not os.getenv("IMPORTGENIUS_API_KEY") and not all_results:
        paid_links.append({
            "source": "importgenius",
            "title": f"ImportGenius — {request.product} ithalatçı kayıtları",
            "url": f"https://www.importgenius.com/importers/{request.product.replace(' ', '-')}",
            "note": "IMPORTGENIUS_API_KEY eklenince otomatik çekilir",
        })
    if not os.getenv("PANJIVA_API_KEY") and not all_results:
        paid_links.append({
            "source": "panjiva",
            "title": f"Panjiva — {request.product} sevkiyat verisi",
            "url": f"https://panjiva.com/search?q={request.product.replace(' ', '+')}",
            "note": "PANJIVA_API_KEY eklenince otomatik çekilir",
        })

    if paid_links:
        all_results.extend(paid_links)
        sources_used.append("paid_links")

    note = None
    if not sources_used or sources_used == ["paid_links"]:
        note = "ScraperAPI key ekleyin → Thomasnet gerçek verisi için"

    return MarketSearchResponse(
        results=all_results,
        total=len(all_results),
        market="usa",
        sources_used=sources_used or ["thomasnet", "importgenius", "panjiva"],
        note=note,
    )


# ─── UN Comtrade Direct Endpoint ─────────────────────────────────────────────

@router.get("/trade-data")
async def get_trade_data(
    hs_code: str,
    reporter: str = "all",
    partner: str = "all",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """UN Comtrade ücretsiz resmi ticaret verisi"""
    data = await _fetch_un_comtrade(hs_code, reporter, partner)
    return {"data": data, "total": len(data), "source": "un_comtrade", "hs_code": hs_code}


# ─── Market Compare ───────────────────────────────────────────────────────────

@router.get("/compare")
async def compare_markets(
    product: str,
    markets: str = "china,usa",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """İki pazarı karşılaştır (özet istatistik)"""
    return {
        "product": product,
        "markets_compared": markets.split(","),
        "note": "Detaylı karşılaştırma için /china/search ve /usa/search kullanın",
    }
