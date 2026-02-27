"""
B2B Platform Scraping Servisleri
ScraperAPI + BeautifulSoup kullanır.
Key olmadan → doğrudan arama linkleri döner (fallback).

Platformlar:
  Çin:   Alibaba, Made-in-China, DHgate, AliExpress, 1688, Global Sources, Yiwugo
  Dünya: TradeKey, EC21, IndiaMart, TradeIndia, ECPlaza, Kompass, Thomasnet
"""

import httpx
import asyncio
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import os
from urllib.parse import quote_plus, urljoin


# ─────────────────────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    """DB önce, sonra env'den ScraperAPI key al"""
    try:
        from app.core.database import SessionLocal
        from app.models.api_setting import ApiSetting
        import base64
        db = SessionLocal()
        s = db.query(ApiSetting).filter(ApiSetting.key_name == "SCRAPERAPI_KEY").first()
        db.close()
        if s and s.key_value:
            return base64.b64decode(s.key_value.encode()).decode()
    except Exception:
        pass
    return os.getenv("SCRAPERAPI_KEY", "")


def _scraperapi_url(url: str, api_key: str, render: bool = False, country: str = "") -> str:
    """ScraperAPI proxy URL oluştur"""
    base = f"http://api.scraperapi.com/?api_key={api_key}&url={quote_plus(url)}"
    if render:
        base += "&render=true"
    if country:
        base += f"&country_code={country}"
    return base


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def _fetch(url: str, api_key: str = "", render: bool = False, country: str = "") -> Optional[str]:
    """URL'den HTML çek. api_key varsa ScraperAPI üzerinden."""
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            target = _scraperapi_url(url, api_key, render, country) if api_key else url
            r = await client.get(target, headers=HEADERS)
            if r.status_code == 200:
                return r.text
            print(f"[fetch] {url} → HTTP {r.status_code}")
    except Exception as e:
        print(f"[fetch] {url}: {e}")
    return None


def _link(query: str, base: str) -> str:
    return base + quote_plus(query)


# ─────────────────────────────────────────────────────────────────────────────
# 1. ALİBABA.COM
# ─────────────────────────────────────────────────────────────────────────────

class AlibabaScraper:
    """Alibaba.com — dünyanın en büyük B2B platformu"""

    BASE = "https://www.alibaba.com/trade/search?SearchText={q}&IndexArea=product_en"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = AlibabaScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key, render=False)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            selectors = [
                ".m-gallery-product-item-v2",
                ".J-offer-wrapper",
                ".organic-list-offer-outter",
                "[class*='oVvSg_']",   # yeni Alibaba layout
                ".product-snippet",
            ]
            cards = []
            for sel in selectors:
                cards = soup.select(sel)[:max_results]
                if cards:
                    break

            for card in cards:
                try:
                    title_el = card.select_one(
                        ".elements-title-normal__oSoze, .title, h2, [class*='title']"
                    )
                    price_el = card.select_one(
                        ".elements-offer-price-normal__price, .price, [class*='price']"
                    )
                    supplier_el = card.select_one(
                        ".elements-supplier-name__matxT, .company-name, [class*='supplier']"
                    )
                    link_el = card.select_one("a[href]")
                    img_el = card.select_one("img[src], img[data-src]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if href.startswith("//"):
                        href = "https:" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Tedarikçiye sorun",
                        "supplier": supplier_el.get_text(strip=True) if supplier_el else "Verified Supplier",
                        "image_url": (img_el.get("src") or img_el.get("data-src", "")) if img_el else "",
                        "product_url": href,
                        "source": "alibaba",
                        "country": "China",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — Alibaba.com Ürün Araması",
                "price": "Tedarikçiye sorun",
                "supplier": "Verified Supplier",
                "image_url": "",
                "product_url": url,
                "source": "alibaba",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 2. MADE-IN-CHINA.COM
# ─────────────────────────────────────────────────────────────────────────────

class MadeInChinaScraper:
    """Made-in-China.com — doğrulanmış Çin üreticileri"""

    BASE = "https://www.made-in-china.com/products-search/hot-china-products/{q}.html"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = MadeInChinaScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".product-info, .J-product-item, .item-main, .product-container")[:max_results]:
                try:
                    title_el = card.select_one(".title a, h4 a, .pro-name, [class*='title']")
                    price_el = card.select_one(".price, .product-price, [class*='price']")
                    supplier_el = card.select_one(".company-name, .by-company, [class*='company']")
                    link_el = card.select_one("a[href]")
                    img_el = card.select_one("img[src], img[data-src]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if href.startswith("//"):
                        href = "https:" + href
                    elif not href.startswith("http"):
                        href = "https://www.made-in-china.com" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Contact",
                        "supplier": supplier_el.get_text(strip=True) if supplier_el else "Verified Manufacturer",
                        "image_url": (img_el.get("src") or img_el.get("data-src", "")) if img_el else "",
                        "product_url": href,
                        "source": "made-in-china",
                        "country": "China",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — Made-in-China.com",
                "price": "Contact supplier",
                "supplier": "Verified Manufacturer",
                "image_url": "",
                "product_url": url,
                "source": "made-in-china",
                "country": "China",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 3. DHGATE.COM
# ─────────────────────────────────────────────────────────────────────────────

class DHgateScraper:
    """DHgate.com — düşük MOQ, dropshipping dostu"""

    BASE = "https://www.dhgate.com/wholesale/search.do?act=search&searchkey={q}"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = DHgateScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".item.gallery-item, .proInfo, .item-block, [class*='product']")[:max_results]:
                try:
                    title_el = card.select_one(".item-title a, .proName, .title a, [class*='title'] a")
                    price_el = card.select_one(".item-price, .price, [class*='price']")
                    link_el = card.select_one("a[href]")
                    img_el = card.select_one("img[src], img[data-src]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if href.startswith("//"):
                        href = "https:" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Contact",
                        "image_url": (img_el.get("src") or img_el.get("data-src", "")) if img_el else "",
                        "product_url": href,
                        "source": "dhgate",
                        "country": "China",
                        "note": "Low MOQ",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — DHgate",
                "price": "Contact supplier",
                "image_url": "",
                "product_url": url,
                "source": "dhgate",
                "country": "China",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 4. ALİEXPRESS.COM
# ─────────────────────────────────────────────────────────────────────────────

class AliExpressScraper:
    """AliExpress — perakende/dropshipping, düşük MOQ"""

    BASE = "https://www.aliexpress.com/wholesale?SearchText={q}"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = AliExpressScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key, render=True)  # JS render gerekli
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".product-item, ._1AtVbE, [class*='product']")[:max_results]:
                try:
                    title_el = card.select_one("h1, .title, a[title]")
                    price_el = card.select_one(".price, [class*='price']")
                    link_el = card.select_one("a[href]")
                    img_el = card.select_one("img[src], img[data-src]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title or len(title) < 5:
                        continue

                    href = link_el["href"] if link_el else url
                    if href.startswith("//"):
                        href = "https:" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Contact",
                        "image_url": (img_el.get("src") or img_el.get("data-src", "")) if img_el else "",
                        "product_url": href,
                        "source": "aliexpress",
                        "country": "China",
                        "note": "No MOQ — dropshipping",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — AliExpress",
                "price": "Retail price",
                "image_url": "",
                "product_url": url,
                "source": "aliexpress",
                "country": "China",
                "note": "Toptan için Alibaba.com kullanın",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 5. 1688.COM (Çin iç pazarı)
# ─────────────────────────────────────────────────────────────────────────────

class Alibaba1688Scraper:
    """1688.com — Çin iç pazarı, fabrika fiyatı (ScraperAPI render gerekli)"""

    BASE = "https://s.1688.com/selloffer/offer_search.htm?keywords={q}"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = Alibaba1688Scraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key, render=True, country="cn")
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".card-offer, .sm-offer-item, [class*='offer']")[:max_results]:
                try:
                    title_el = card.select_one(".title, [class*='title'], a[title]")
                    price_el = card.select_one(".price, [class*='price']")
                    link_el = card.select_one("a[href]")
                    img_el = card.select_one("img[src], img[data-src]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if href.startswith("//"):
                        href = "https:" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Factory price",
                        "image_url": (img_el.get("src") or img_el.get("data-src", "")) if img_el else "",
                        "product_url": href,
                        "source": "1688",
                        "country": "China",
                        "note": "Alibaba'dan %30-50 ucuz — sourcing agent gerekebilir",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — 1688.com Fabrika Fiyatı",
                "price": "%30-50 cheaper than Alibaba",
                "image_url": "",
                "product_url": url,
                "source": "1688",
                "country": "China",
                "note": "ScraperAPI key ekleyin + Çinçe arama terimi önerilir",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 6. GLOBAL SOURCES
# ─────────────────────────────────────────────────────────────────────────────

class GlobalSourcesScraper:
    """GlobalSources.com — doğrulanmış ihracatçılar, CE/ISO sertifikalı"""

    BASE = "https://www.globalsources.com/SEARCH/s?query={q}"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = GlobalSourcesScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".product-cell, .item-cell, [class*='product']")[:max_results]:
                try:
                    title_el = card.select_one(".product-title, .title, a[title]")
                    price_el = card.select_one(".price, [class*='price']")
                    supplier_el = card.select_one(".supplier-name, [class*='supplier']")
                    link_el = card.select_one("a[href]")
                    img_el = card.select_one("img[src]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if not href.startswith("http"):
                        href = "https://www.globalsources.com" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Contact",
                        "supplier": supplier_el.get_text(strip=True) if supplier_el else "Verified Supplier",
                        "image_url": img_el["src"] if img_el else "",
                        "product_url": href,
                        "source": "global-sources",
                        "country": "China",
                        "note": "CE / ISO doğrulanmış",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — Global Sources",
                "price": "Contact supplier",
                "supplier": "Verified Premium Supplier",
                "image_url": "",
                "product_url": url,
                "source": "global-sources",
                "country": "China",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 7. TRADEKEY.COM (RFQ / Buying Leads)
# ─────────────────────────────────────────────────────────────────────────────

class TradeKeyScraper:
    """TradeKey.com — küresel alım ilanları (RFQ)"""

    BASE = "https://www.tradekey.com/buying-leads/{q}.html"

    @staticmethod
    async def search_rfqs(query: str, country: str = "", max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = TradeKeyScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".rfq-list-item, .lead-item, .buying-lead, [class*='rfq']")[:max_results]:
                try:
                    title_el = card.select_one(".rfq-title, .title, h3, [class*='title']")
                    company_el = card.select_one(".company-name, .company, [class*='company']")
                    country_el = card.select_one(".country, .location, [class*='country']")
                    qty_el = card.select_one(".quantity, .qty, [class*='qty']")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    results.append({
                        "title": title[:200],
                        "company": company_el.get_text(strip=True) if company_el else "Buyer",
                        "country": country_el.get_text(strip=True) if country_el else (country or "Global"),
                        "quantity": qty_el.get_text(strip=True) if qty_el else "Contact",
                        "source": "tradekey",
                        "type": "RFQ / Buying Lead",
                        "url": url,
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — TradeKey Alım İlanları",
                "company": "Global Buyer",
                "country": country or "Global",
                "quantity": "Contact",
                "source": "tradekey",
                "type": "RFQ / Buying Lead",
                "url": url,
                "note": "ScraperAPI key ekleyin → gerçek alım ilanları görünür",
            }]

        return results[:max_results]

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        """Ürün araması (RFQ ile aynı endpoint'i kullan)"""
        return await TradeKeyScraper.search_rfqs(query, max_results=max_results)


# ─────────────────────────────────────────────────────────────────────────────
# 8. EC21.COM
# ─────────────────────────────────────────────────────────────────────────────

class EC21Scraper:
    """EC21.com — küresel B2B, Kore ağırlıklı"""

    BASE = "https://www.ec21.com/search/global/{q}"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = EC21Scraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".prod_item, .product-item, .prd, [class*='prod']")[:max_results]:
                try:
                    title_el = card.select_one(".product-title, .tit, h3, [class*='title']")
                    price_el = card.select_one(".price, .prc, [class*='price']")
                    supplier_el = card.select_one(".company-name, .comp, [class*='company']")
                    country_el = card.select_one(".country, [class*='country']")
                    link_el = card.select_one("a[href]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if not href.startswith("http"):
                        href = "https://www.ec21.com" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "FOB Contact",
                        "supplier": supplier_el.get_text(strip=True) if supplier_el else "Supplier",
                        "country": country_el.get_text(strip=True) if country_el else "Korea/Global",
                        "product_url": href,
                        "source": "ec21",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — EC21 Global B2B",
                "price": "FOB Contact",
                "supplier": "Verified Supplier",
                "country": "Korea/Global",
                "product_url": url,
                "source": "ec21",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]

    @staticmethod
    async def search_by_oem(oem_number: str, max_results: int = 20) -> List[Dict]:
        return await EC21Scraper.search_products(oem_number, max_results)


# ─────────────────────────────────────────────────────────────────────────────
# 9. INDIAMART
# ─────────────────────────────────────────────────────────────────────────────

class IndiaMARTScraper:
    """IndiaMart.com — Hindistan'ın en büyük B2B platformu"""

    BASE = "https://dir.indiamart.com/search.mp?ss={q}"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = IndiaMARTScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".product-unit, .prd-blk, .p-unit, [class*='product']")[:max_results]:
                try:
                    title_el = card.select_one(".puT, .tit, .pTit, h3, [class*='title']")
                    price_el = card.select_one(".price, .prc, [class*='price']")
                    company_el = card.select_one(".company-name, .companyNm, [class*='company']")
                    link_el = card.select_one("a[href]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if not href.startswith("http"):
                        href = "https://dir.indiamart.com" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "₹ Contact",
                        "supplier": company_el.get_text(strip=True) if company_el else "Indian Manufacturer",
                        "country": "India",
                        "product_url": href,
                        "source": "indiamart",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — IndiaMart Manufacturer",
                "price": "₹ Contact for price",
                "supplier": "Indian Manufacturer",
                "country": "India",
                "product_url": url,
                "source": "indiamart",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 10. TRADEINDIA.COM
# ─────────────────────────────────────────────────────────────────────────────

class TradeIndiaScraper:
    """TradeIndia.com — Hindistan ihracatçıları"""

    BASE = "https://www.tradeindia.com/search.html?ss={q}"

    @staticmethod
    async def search_exporters(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = TradeIndiaScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".product-list, .prd-item, [class*='product']")[:max_results]:
                try:
                    title_el = card.select_one(".product-name, .title, h3")
                    price_el = card.select_one(".price, [class*='price']")
                    company_el = card.select_one(".company-name, [class*='company']")
                    link_el = card.select_one("a[href]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if not href.startswith("http"):
                        href = "https://www.tradeindia.com" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Contact",
                        "supplier": company_el.get_text(strip=True) if company_el else "Indian Exporter",
                        "country": "India",
                        "product_url": href,
                        "source": "tradeindia",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} Exporter — TradeIndia",
                "price": "Contact",
                "supplier": "Indian Exporter",
                "country": "India",
                "product_url": url,
                "source": "tradeindia",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        return await TradeIndiaScraper.search_exporters(query, max_results)


# ─────────────────────────────────────────────────────────────────────────────
# 11. ECPLAZA.NET (Kore)
# ─────────────────────────────────────────────────────────────────────────────

class ECPlazaScraper:
    """ECPlaza.net — Kore & Asya B2B ağı"""

    BASE = "https://www.ecplaza.net/search/products?keywords={q}"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = ECPlazaScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".item, .product, [class*='item']")[:max_results]:
                try:
                    title_el = card.select_one(".product-name, .name, h3, a[title]")
                    price_el = card.select_one(".price, [class*='price']")
                    company_el = card.select_one(".company, [class*='company']")
                    link_el = card.select_one("a[href]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    href = link_el["href"] if link_el else url
                    if not href.startswith("http"):
                        href = "https://www.ecplaza.net" + href

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Contact",
                        "supplier": company_el.get_text(strip=True) if company_el else "Korean Supplier",
                        "country": "South Korea",
                        "product_url": href,
                        "source": "ecplaza",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — ECPlaza Korean Supplier",
                "price": "Contact",
                "supplier": "Korean Supplier",
                "country": "South Korea",
                "product_url": url,
                "source": "ecplaza",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 12. KOMPASS.COM (Avrupa)
# ─────────────────────────────────────────────────────────────────────────────

class KompassScraper:
    """Kompass.com — Avrupa, dünya çapında firma rehberi"""

    BASE = "https://www.kompass.com/selectcountry/en/search?text={q}"

    @staticmethod
    async def search_companies(query: str, country: str = "", max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = KompassScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".company-card, .result-item, [class*='company']")[:max_results]:
                try:
                    name_el = card.select_one(".company-name, h2, h3, [class*='name']")
                    country_el = card.select_one(".country, .location, [class*='country']")
                    activity_el = card.select_one(".activity, .description, [class*='activity']")
                    link_el = card.select_one("a[href]")

                    name = name_el.get_text(strip=True) if name_el else ""
                    if not name:
                        continue

                    href = link_el["href"] if link_el else url
                    if not href.startswith("http"):
                        href = "https://www.kompass.com" + href

                    results.append({
                        "company": name[:200],
                        "country": country_el.get_text(strip=True) if country_el else (country or "Europe"),
                        "activity": activity_el.get_text(strip=True)[:200] if activity_el else "",
                        "product_url": href,
                        "source": "kompass",
                        "type": "Firma Rehberi",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "company": f"{query} — Kompass Firma Rehberi",
                "country": country or "Europe",
                "activity": "Global trade directory",
                "product_url": url,
                "source": "kompass",
                "type": "Firma Rehberi",
                "note": "ScraperAPI key ekleyin → gerçek firmalar görünür",
            }]

        return results[:max_results]

    @staticmethod
    async def search_european_companies(query: str, country: str = None, max_results: int = 20) -> List[Dict]:
        return await KompassScraper.search_companies(query, country or "", max_results)

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        return await KompassScraper.search_companies(query, max_results=max_results)


# ─────────────────────────────────────────────────────────────────────────────
# 13. THOMASNET.COM (ABD)
# ─────────────────────────────────────────────────────────────────────────────

class ThomasnetScraper:
    """Thomasnet.com — ABD endüstriyel üreticiler, B2B"""

    BASE = "https://www.thomasnet.com/search/?what={q}&where={loc}"

    @staticmethod
    async def search_manufacturers(query: str, location: str = "United+States", max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = ThomasnetScraper.BASE.format(q=quote_plus(query), loc=quote_plus(location))
        html = await _fetch(url, api_key, render=True)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(
                ".profile-card, .supplier-profile-card, [class*='CompanyCard'], [class*='SupplierCard']"
            )[:max_results]:
                try:
                    name_el = card.select_one("h2, h3, [class*='name'], [class*='company']")
                    loc_el = card.select_one("[class*='location'], [class*='city']")
                    desc_el = card.select_one("[class*='description'], p")
                    link_el = card.select_one("a[href]")

                    name = name_el.get_text(strip=True) if name_el else ""
                    if not name:
                        continue

                    href = link_el["href"] if link_el else url
                    if href.startswith("/"):
                        href = "https://www.thomasnet.com" + href

                    results.append({
                        "company": name[:200],
                        "location": loc_el.get_text(strip=True) if loc_el else location,
                        "description": desc_el.get_text(strip=True)[:200] if desc_el else "",
                        "country": "USA",
                        "product_url": href,
                        "source": "thomasnet",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "company": f"{query} Manufacturing Inc.",
                "location": location or "USA",
                "description": "Industrial manufacturer",
                "country": "USA",
                "product_url": url,
                "source": "thomasnet",
                "note": "ScraperAPI key ekleyin → gerçek firmalar görünür",
            }]

        return results[:max_results]

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        return await ThomasnetScraper.search_manufacturers(query, max_results=max_results)


# ─────────────────────────────────────────────────────────────────────────────
# 14. YIWUGO.COM
# ─────────────────────────────────────────────────────────────────────────────

class YiwugoScraper:
    """Yiwugo.com — Çin Yiwu pazarı, küçük parça toptan"""

    BASE = "https://www.yiwugo.com/product/search.html?keyword={q}"

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        api_key = get_api_key()
        url = YiwugoScraper.BASE.format(q=quote_plus(query))
        html = await _fetch(url, api_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".product-item, .item, [class*='product']")[:max_results]:
                try:
                    title_el = card.select_one(".product-name, .name, h3")
                    price_el = card.select_one(".price, [class*='price']")
                    link_el = card.select_one("a[href]")
                    img_el = card.select_one("img[src]")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    results.append({
                        "title": title[:200],
                        "price": price_el.get_text(strip=True) if price_el else "Ultra-competitive",
                        "image_url": img_el["src"] if img_el else "",
                        "product_url": link_el["href"] if link_el else url,
                        "source": "yiwugo",
                        "country": "China",
                        "note": "Yiwu market — world's largest small-commodity market",
                    })
                except Exception:
                    continue

        if not results:
            results = [{
                "title": f"{query} — Yiwu Market",
                "price": "Ultra-competitive (factory direct)",
                "image_url": "",
                "product_url": url,
                "source": "yiwugo",
                "country": "China",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
            }]

        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# 15. IMPORTGENIUS / PANJİVA (Link — ücretli servis)
# ─────────────────────────────────────────────────────────────────────────────

class ImportGeniusScraper:
    """ImportGenius — ABD ithalat gümrük beyanı arama (ücretli servis)"""

    @staticmethod
    async def search_imports(query: str, country: str = "us") -> List[Dict]:
        url = f"https://www.importgenius.com/search?q={quote_plus(query)}&country={country}"
        panjiva = f"https://panjiva.com/search?q={quote_plus(query)}&country[]={country.upper()}"
        return [
            {
                "title": f"{query} — ImportGenius ABD İthalat Kayıtları",
                "company": "ImportGenius.com",
                "country": "USA",
                "url": url,
                "source": "importgenius",
                "type": "Gümrük Beyanı DB",
                "note": "Üyelik gerektirir (importgenius.com)",
            },
            {
                "title": f"{query} — Panjiva Tedarik Zinciri",
                "company": "Panjiva.com (S&P Global)",
                "country": "USA",
                "url": panjiva,
                "source": "panjiva",
                "type": "Gümrük Beyanı DB",
                "note": "Üyelik gerektirir (panjiva.com)",
            },
        ]


# ─────────────────────────────────────────────────────────────────────────────
# ANA SERVİS — Tüm platformları birleştir
# ─────────────────────────────────────────────────────────────────────────────

class TradeAtlasScraper:
    """TradeAtlas — Türk gümrük veri servisi (API aboneliği gerekli)"""

    @staticmethod
    async def search_shipments(query: str, country: Optional[str] = None) -> List[Dict]:
        url = f"https://www.tradeatlas.com/en/search?q={quote_plus(query)}"
        return [{
            "shipper": query,
            "country": country or "Global",
            "url": url,
            "source": "tradeatlas",
            "note": "TradeAtlas API aboneliği gerektirir — tradeatlas.com",
        }]


class B2BScraperService:
    """B2B Scraping Orchestrator — tüm platformları yönetir"""

    PLATFORM_MAP = {
        # Çin
        "alibaba":        AlibabaScraper.search_products,
        "made-in-china":  MadeInChinaScraper.search_products,
        "dhgate":         DHgateScraper.search_products,
        "aliexpress":     AliExpressScraper.search_products,
        "1688":           Alibaba1688Scraper.search_products,
        "global-sources": GlobalSourcesScraper.search_products,
        "yiwugo":         YiwugoScraper.search_products,
        # Küresel B2B
        "tradekey":       TradeKeyScraper.search_products,
        "ec21":           EC21Scraper.search_products,
        "indiamart":      IndiaMARTScraper.search_products,
        "tradeindia":     TradeIndiaScraper.search_products,
        "ecplaza":        ECPlazaScraper.search_products,
        "kompass":        KompassScraper.search_products,
        # ABD
        "thomasnet":      ThomasnetScraper.search_products,
    }

    @staticmethod
    async def search_all_platforms(
        search_query: str,
        platforms: List[str] = None,
    ) -> Dict[str, List[Dict]]:
        """Seçili platformlarda eş zamanlı ara"""
        if platforms is None:
            platforms = ["alibaba", "made-in-china", "dhgate", "tradekey", "indiamart"]

        tasks = {}
        for p in platforms:
            if p in B2BScraperService.PLATFORM_MAP:
                tasks[p] = B2BScraperService.PLATFORM_MAP[p](search_query)

        results = {}
        gathered = await asyncio.gather(*tasks.values(), return_exceptions=True)
        for platform, result in zip(tasks.keys(), gathered):
            if isinstance(result, Exception):
                print(f"[B2BScraperService] {platform}: {result}")
                results[platform] = []
            else:
                results[platform] = result

        return results

    @staticmethod
    def get_api_status() -> Dict:
        """ScraperAPI key durumunu döndür"""
        key = get_api_key()
        return {
            "scraperapi_configured": bool(key),
            "key_preview": f"{key[:4]}••••••••{key[-4:]}" if key and len(key) > 8 else None,
            "platforms_available": list(B2BScraperService.PLATFORM_MAP.keys()),
            "note": "Key olmadan fallback link döner, key ile gerçek veri çekilir",
        }
