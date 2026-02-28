"""
B2B Platform Scraping Servisleri
ScraperAPI + BeautifulSoup kullanır.
Key olmadan → doğrudan arama linkleri döner (fallback).

Platformlar:
  Çin:   Alibaba, Made-in-China, DHgate, AliExpress, 1688, Global Sources, Yiwugo
  Dünya: TradeKey, EC21, IndiaMart, TradeIndia, ECPlaza, Kompass, Thomasnet

Değişiklikler (base_scraper.py entegrasyonu):
  - String birleştirme yerine normalize_url() / urljoin kullanıldı
  - _fetch yerine BaseScraper.retry_request() (3 deneme, backoff, rate-limit)
  - except: pass → log_error() ile loglanıyor
  - get_text çıktısı clean_string() ile temizleniyor
"""

import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import quote_plus

from app.services.base_scraper import (
    BaseScraper,
    get_scraperapi_key,
    normalize_url,
    clean_string,
    log_scrape_error,
    try_selectors,
    safe_url,
)


# ─────────────────────────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR (geriye dönük uyumluluk alias'ları)
# ─────────────────────────────────────────────────────────────────────────────

# get_api_key → get_scraperapi_key (base_scraper'dan import edildi)
get_api_key = get_scraperapi_key


async def _fetch(url: str, api_key: str = "", render: bool = False, country: str = "") -> Optional[str]:
    """Geriye dönük uyumluluk: retry_fetch'i kullanır."""
    from app.services.base_scraper import retry_fetch
    return await retry_fetch(url, api_key=api_key, render=render, country=country, module="b2b_scraper")


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
                    title_el = try_selectors(card, [
                        ".elements-title-normal__oSoze",
                        "[data-content='title'] a",
                        ".organic-list-offer__image a",
                        "h2 a", "h2", "[class*='title']",
                    ])
                    price_el = try_selectors(card, [
                        ".elements-offer-price-normal__price",
                        ".price-current",
                        "[data-price]",
                        ".offer-price",
                        "[class*='price']",
                    ])
                    supplier_el = try_selectors(card, [
                        ".elements-supplier-name__matxT",
                        ".company-name",
                        "[class*='supplier']",
                    ])
                    link_el = try_selectors(card, [
                        "[data-content='title'] a[href]",
                        ".organic-list-offer__image a[href]",
                        "h2 a[href]",
                        "a[href]",
                    ])
                    img_el = card.select_one("img[src], img[data-src]")

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.alibaba.com")

                    results.append({
                        "mode": "product_search",
                        "source": "alibaba",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": clean_string(supplier_el.get_text()) if supplier_el else "Verified Supplier",
                        "supplier_country": "China",
                        "image_url": (img_el.get("src") or img_el.get("data-src")) if img_el else None,
                        "relevance_score": 70,
                    })
                except Exception as e:
                    log_scrape_error("alibaba", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "alibaba",
                "product_name": f"{query} — Alibaba.com",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "Verified Supplier",
                "supplier_country": "China",
                "note": "ScraperAPI key ekleyin → gerçek sonuçlar görünür",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".product-name a", ".prom-list-info a", ".title a", "h4 a", ".pro-name", "[class*='title']"])
                    price_el = try_selectors(card, [".price", ".product-price", "[class*='price']"])
                    supplier_el = try_selectors(card, [".company-name", ".by-company", "[class*='company']"])
                    link_el = try_selectors(card, [".product-name a[href]", ".prom-list-info a[href]", "a[href]"])
                    img_el = card.select_one("img[src], img[data-src]")

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.made-in-china.com")

                    results.append({
                        "mode": "product_search",
                        "source": "made-in-china",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": clean_string(supplier_el.get_text()) if supplier_el else "Verified Manufacturer",
                        "supplier_country": "China",
                        "image_url": (img_el.get("src") or img_el.get("data-src")) if img_el else None,
                        "relevance_score": 70,
                    })
                except Exception as e:
                    log_scrape_error("made-in-china", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "made-in-china",
                "product_name": f"{query} — Made-in-China.com",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "Verified Manufacturer",
                "supplier_country": "China",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".item-name a[href]", ".gallery-name a[href]", ".item-title a", ".proName", "[class*='title'] a"])
                    price_el = try_selectors(card, [".item-price", ".price", ".sale-price", "[class*='price']"])
                    link_el = try_selectors(card, [".item-name a[href]", ".gallery-name a[href]", "a[href]"])
                    img_el = card.select_one("img[src], img[data-src]")

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.dhgate.com")

                    results.append({
                        "mode": "product_search",
                        "source": "dhgate",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": "DHgate Seller",
                        "supplier_country": "China",
                        "image_url": (img_el.get("src") or img_el.get("data-src")) if img_el else None,
                        "moq": "Low MOQ",
                        "relevance_score": 65,
                    })
                except Exception as e:
                    log_scrape_error("dhgate", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "dhgate",
                "product_name": f"{query} — DHgate",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "DHgate Seller",
                "supplier_country": "China",
                "moq": "Low MOQ",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, ["a.product-card[href]", "h1", ".title", "a[title]", "[class*='title']"])
                    price_el = try_selectors(card, [".price", "[class*='price']"])
                    link_el = try_selectors(card, ["a.product-card[href]", "a[href]"])
                    img_el = card.select_one("img[src], img[data-src]")

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title or len(title) < 5:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.aliexpress.com")

                    results.append({
                        "mode": "product_search",
                        "source": "aliexpress",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": "AliExpress Seller",
                        "supplier_country": "China",
                        "image_url": (img_el.get("src") or img_el.get("data-src")) if img_el else None,
                        "moq": "No MOQ",
                        "relevance_score": 60,
                    })
                except Exception as e:
                    log_scrape_error("aliexpress", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "aliexpress",
                "product_name": f"{query} — AliExpress",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "AliExpress Seller",
                "supplier_country": "China",
                "moq": "No MOQ",
                "note": "Toptan için Alibaba.com kullanın",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".title", "[class*='title']", "a[title]"])
                    price_el = try_selectors(card, [".price", "[class*='price']"])
                    link_el = try_selectors(card, ["a[href]"])
                    img_el = card.select_one("img[src], img[data-src]")

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://s.1688.com")

                    results.append({
                        "mode": "product_search",
                        "source": "1688",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": "1688 Fabrikasi",
                        "supplier_country": "China",
                        "image_url": (img_el.get("src") or img_el.get("data-src")) if img_el else None,
                        "note": "Alibaba'dan %30-50 ucuz",
                        "relevance_score": 75,
                    })
                except Exception as e:
                    log_scrape_error("1688", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "1688",
                "product_name": f"{query} — 1688.com Fabrika Fiyatı",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "1688 Fabrikasi",
                "supplier_country": "China",
                "note": "ScraperAPI key + Çince arama terimi önerilir",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".product-name a", ".prd-title a", ".product-title", ".title", "a[title]"])
                    price_el = try_selectors(card, [".price", "[class*='price']"])
                    supplier_el = try_selectors(card, [".supplier-name", "[class*='supplier']"])
                    cert_els = card.select(".cert-icon")
                    link_el = try_selectors(card, [".product-name a[href]", ".prd-title a[href]", "a[href]"])
                    img_el = card.select_one("img[src]")

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.globalsources.com")
                    certs = [c.get("alt", "") for c in cert_els if c.get("alt")]

                    results.append({
                        "mode": "product_search",
                        "source": "global-sources",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": clean_string(supplier_el.get_text()) if supplier_el else "Verified Premium Supplier",
                        "supplier_country": "China",
                        "certifications": certs,
                        "image_url": img_el["src"] if img_el else None,
                        "relevance_score": 75,
                    })
                except Exception as e:
                    log_scrape_error("global-sources", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "global-sources",
                "product_name": f"{query} — Global Sources",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "Verified Premium Supplier",
                "supplier_country": "China",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".rfq-title a", ".rfq-title", ".title", "h3", "[class*='title']"])
                    company_el = try_selectors(card, [".company-name", ".company", "[class*='company']"])
                    country_el = try_selectors(card, [".country", ".location", "[class*='country']"])
                    qty_el = try_selectors(card, [".quantity", ".qty", "[class*='qty']"])
                    date_el = try_selectors(card, ["[data-date]", ".post-date", ".date"])
                    link_el = try_selectors(card, [".rfq-title a[href]", "a[href]"])

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.tradekey.com")

                    results.append({
                        "mode": "rfq_search",
                        "source": "tradekey",
                        "rfq_title": title[:200],
                        "rfq_url": href,
                        "url_status": None,
                        "buyer_name": clean_string(company_el.get_text()) if company_el else "Global Buyer",
                        "buyer_country": clean_string(country_el.get_text()) if country_el else (country or "Global"),
                        "quantity_needed": clean_string(qty_el.get_text()) if qty_el else None,
                        "posted_date": (date_el.get("data-date") or clean_string(date_el.get_text())) if date_el else None,
                        "relevance_score": 70,
                    })
                except Exception as e:
                    log_scrape_error("tradekey", str(e))
                    continue

        if not results:
            results = [{
                "mode": "rfq_search",
                "source": "tradekey",
                "rfq_title": f"{query} — TradeKey Alım İlanları",
                "rfq_url": url,
                "url_status": None,
                "buyer_name": "Global Buyer",
                "buyer_country": country or "Global",
                "note": "ScraperAPI key ekleyin → gerçek alım ilanları görünür",
                "relevance_score": 30,
            }]

        return results[:max_results]

    @staticmethod
    async def search_products(query: str, max_results: int = 20) -> List[Dict]:
        """Ürün araması — RFQ moduna yönlendir"""
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
                    title_el = try_selectors(card, [".product-title", ".tit", "h3", "[class*='title']"])
                    price_el = try_selectors(card, [".price", ".prc", "[class*='price']"])
                    supplier_el = try_selectors(card, [".company-name", ".comp", "[class*='company']"])
                    country_el = try_selectors(card, [".country", "[class*='country']"])
                    link_el = try_selectors(card, [".pname a[href]", ".product-list a[href]", "a[href]"])

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.ec21.com")

                    results.append({
                        "mode": "product_search",
                        "source": "ec21",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": clean_string(supplier_el.get_text()) if supplier_el else "Supplier",
                        "supplier_country": clean_string(country_el.get_text()) if country_el else "Korea/Global",
                        "relevance_score": 70,
                    })
                except Exception as e:
                    log_scrape_error("ec21", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "ec21",
                "product_name": f"{query} — EC21 Global B2B",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "Verified Supplier",
                "supplier_country": "Korea/Global",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".puT", ".tit", ".pTit", "h3", "[class*='title']"])
                    price_el = try_selectors(card, [".price", ".prc", "[class*='price']"])
                    company_el = try_selectors(card, [".company-name", ".companyNm", "[class*='company']"])
                    link_el = try_selectors(card, [".product-name a[href]", "h3 a[href]", "a[href]"])

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://dir.indiamart.com")

                    results.append({
                        "mode": "product_search",
                        "source": "indiamart",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": clean_string(company_el.get_text()) if company_el else "Indian Manufacturer",
                        "supplier_country": "India",
                        "relevance_score": 70,
                    })
                except Exception as e:
                    log_scrape_error("indiamart", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "indiamart",
                "product_name": f"{query} — IndiaMart",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "Indian Manufacturer",
                "supplier_country": "India",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".product-name", ".title", "h3"])
                    price_el = try_selectors(card, [".price", "[class*='price']"])
                    company_el = try_selectors(card, [".company-name", "[class*='company']"])
                    link_el = try_selectors(card, [".product-name a[href]", "h3 a[href]", "a[href]"])

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.tradeindia.com")

                    results.append({
                        "mode": "product_search",
                        "source": "tradeindia",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": clean_string(company_el.get_text()) if company_el else "Indian Exporter",
                        "supplier_country": "India",
                        "relevance_score": 65,
                    })
                except Exception as e:
                    log_scrape_error("tradeindia", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "tradeindia",
                "product_name": f"{query} Exporter — TradeIndia",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "Indian Exporter",
                "supplier_country": "India",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".product-name", ".name", "h3", "a[title]"])
                    price_el = try_selectors(card, [".price", "[class*='price']"])
                    company_el = try_selectors(card, [".company", "[class*='company']"])
                    link_el = try_selectors(card, [".product-name a[href]", "a[title][href]", "a[href]"])

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.ecplaza.net")

                    results.append({
                        "mode": "product_search",
                        "source": "ecplaza",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": clean_string(company_el.get_text()) if company_el else "Korean Supplier",
                        "supplier_country": "South Korea",
                        "relevance_score": 65,
                    })
                except Exception as e:
                    log_scrape_error("ecplaza", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "ecplaza",
                "product_name": f"{query} — ECPlaza Korean Supplier",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "Korean Supplier",
                "supplier_country": "South Korea",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
                "relevance_score": 30,
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
                    name_el = try_selectors(card, [".company-name", "h2", "h3", "[class*='name']"])
                    country_el = try_selectors(card, [".country", ".location", "[class*='country']"])
                    activity_el = try_selectors(card, [".activity", ".description", "[class*='activity']"])
                    link_el = try_selectors(card, [".company-name a[href]", "h2 a[href]", "a[href]"])

                    name = clean_string(name_el.get_text()) if name_el else ""
                    if not name:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.kompass.com")

                    results.append({
                        "mode": "product_search",
                        "source": "kompass",
                        "product_name": name[:200],
                        "product_url": href,
                        "url_status": None,
                        "supplier_name": name[:200],
                        "supplier_country": clean_string(country_el.get_text()) if country_el else (country or "Europe"),
                        "description": clean_string(activity_el.get_text())[:200] if activity_el else None,
                        "relevance_score": 70,
                    })
                except Exception as e:
                    log_scrape_error("kompass", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "kompass",
                "product_name": f"{query} — Kompass Firma Rehberi",
                "product_url": url,
                "url_status": None,
                "supplier_name": query,
                "supplier_country": country or "Europe",
                "note": "ScraperAPI key ekleyin → gerçek firmalar görünür",
                "relevance_score": 30,
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
                    name_el = try_selectors(card, ["h2", "h3", "[class*='name']", "[class*='company']"])
                    loc_el = try_selectors(card, ["[class*='location']", "[class*='city']"])
                    desc_el = try_selectors(card, ["[class*='description']", "p"])
                    link_el = try_selectors(card, ["h2 a[href]", "h3 a[href]", "a[href]"])

                    name = clean_string(name_el.get_text()) if name_el else ""
                    if not name:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.thomasnet.com")

                    results.append({
                        "mode": "product_search",
                        "source": "thomasnet",
                        "product_name": name[:200],
                        "product_url": href,
                        "url_status": None,
                        "supplier_name": name[:200],
                        "supplier_country": "USA",
                        "location": clean_string(loc_el.get_text()) if loc_el else location,
                        "description": clean_string(desc_el.get_text())[:200] if desc_el else None,
                        "relevance_score": 80,
                    })
                except Exception as e:
                    log_scrape_error("thomasnet", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "thomasnet",
                "product_name": f"{query} Manufacturing Inc.",
                "product_url": url,
                "url_status": None,
                "supplier_name": f"{query} Manufacturing Inc.",
                "supplier_country": "USA",
                "location": location or "USA",
                "note": "ScraperAPI key ekleyin → gerçek firmalar görünür",
                "relevance_score": 30,
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
                    title_el = try_selectors(card, [".product-name", ".name", "h3"])
                    price_el = try_selectors(card, [".price", "[class*='price']"])
                    link_el = try_selectors(card, [".product-name a[href]", "a[href]"])
                    img_el = card.select_one("img[src]")

                    title = clean_string(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    href = safe_url(link_el.get("href", "") if link_el else "", "https://www.yiwugo.com")

                    results.append({
                        "mode": "product_search",
                        "source": "yiwugo",
                        "product_name": title[:200],
                        "product_url": href,
                        "url_status": None,
                        "price": clean_string(price_el.get_text()) if price_el else None,
                        "supplier_name": "Yiwu Market Seller",
                        "supplier_country": "China",
                        "image_url": img_el["src"] if img_el else None,
                        "note": "Yiwu market — world's largest small-commodity market",
                        "relevance_score": 65,
                    })
                except Exception as e:
                    log_scrape_error("yiwugo", str(e))
                    continue

        if not results:
            results = [{
                "mode": "product_search",
                "source": "yiwugo",
                "product_name": f"{query} — Yiwu Market",
                "product_url": url,
                "url_status": None,
                "price": None,
                "supplier_name": "Yiwu Market Seller",
                "supplier_country": "China",
                "note": "ScraperAPI key ekleyin → gerçek ilanlar görünür",
                "relevance_score": 30,
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
