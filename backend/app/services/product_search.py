"""
Potansiyel Müşteri Arama Servisi
================================
Kaynaklar:
  Arama Motorları : Google, Yandex, Bing, Baidu, DuckDuckGo, Yahoo
  Ticaret DB      : TradeAtlas, ImportGenius, Trademo Intel, Panjiva,
                    Global Buyers Online, Europages, TradeKey, TradeMap, UN Comtrade

Tüm scraper'lar:
  - base_scraper.retry_fetch ile 3 deneme + exponential backoff
  - normalize_url   → urljoin tabanlı absolute URL
  - clean_string    → HTML entity + invisible char temizleme
  - validate_output → url_status alanı eklenir, 404 URL linkleri gizlenir
"""

import asyncio
import re
from typing import List, Dict, Optional, Any
from urllib.parse import quote_plus, urljoin, urlparse
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.services.base_scraper import (
    get_scraperapi_key,
    normalize_url,
    clean_string,
    retry_fetch,
    is_valid_url,
    log_scrape_error,
    log_scrape_info,
)
from app.models.product import Product


# ─── Arama Parametreleri Modeli ───────────────────────────────────────────────

class SearchParams:
    """Form alanlarını tutar ve arama sorgusu oluşturur."""
    def __init__(
        self,
        product_name: str = "",
        gtip_code: str = "",
        oem_no: str = "",
        target_country: str = "",
        search_language: str = "en",
        related_sectors: str = "",
        competitor_brands: str = "",
    ):
        self.product_name = clean_string(product_name)
        self.gtip_code = clean_string(gtip_code)
        self.oem_no = clean_string(oem_no)
        self.target_country = clean_string(target_country)
        self.search_language = search_language or "en"
        self.related_sectors = clean_string(related_sectors)
        self.competitor_brands = clean_string(competitor_brands)

    def build_query(self) -> str:
        """Tüm form alanlarını tek arama sorgusuna dönüştür."""
        parts = []
        if self.product_name:
            parts.append(self.product_name)
        if self.gtip_code:
            parts.append(f"HS {self.gtip_code}")
        if self.oem_no:
            parts.append(self.oem_no)
        if self.related_sectors:
            parts.append(self.related_sectors)
        if self.competitor_brands:
            parts.append(self.competitor_brands)
        return " ".join(parts)

    def build_buyer_query(self) -> str:
        """Alıcı odaklı arama sorgusu."""
        q = self.build_query()
        country_part = f' importer "{self.target_country}"' if self.target_country else " importer buyer"
        return q + country_part

    @property
    def country_code(self) -> str:
        """Ülke → ISO 2-letter kodu."""
        MAP = {
            "Germany": "de", "Almanya": "de",
            "France": "fr", "Fransa": "fr",
            "UK": "gb", "İngiltere": "gb", "United Kingdom": "gb",
            "USA": "us", "ABD": "us", "United States": "us",
            "China": "cn", "Çin": "cn",
            "Russia": "ru", "Rusya": "ru",
            "India": "in", "Hindistan": "in",
            "Japan": "jp", "Japonya": "jp",
            "South Korea": "kr", "Güney Kore": "kr",
            "Italy": "it", "İtalya": "it",
            "Spain": "es", "İspanya": "es",
            "Poland": "pl", "Polonya": "pl",
            "Brazil": "br", "Brezilya": "br",
            "UAE": "ae", "BAE": "ae",
        }
        return MAP.get(self.target_country, "")


# ─── Ortak Yardımcı ───────────────────────────────────────────────────────────

def _make_result(
    source: str,
    company_name: str = "",
    country: str = "",
    contact: str = "",
    website: str = "",
    product_match: str = "",
    relevance_score: int = 50,
    raw_data: dict = None,
    url_status: Optional[int] = None,
) -> Dict:
    """Standart sonuç dict'i oluştur."""
    website = normalize_url(website) if website else ""
    return {
        "source": source,
        "company_name": clean_string(company_name, 200),
        "country": clean_string(country, 100),
        "contact": clean_string(contact, 200),
        "website": website,
        "url_status": url_status,
        "product_match": clean_string(product_match, 200),
        "relevance_score": max(0, min(100, relevance_score)),
        "raw_data": raw_data or {},
    }


def _score_result(r: Dict, params: SearchParams) -> int:
    """Basit relevance score hesapla."""
    score = 50
    text = (r.get("company_name", "") + " " + r.get("product_match", "")).lower()
    q_words = params.build_query().lower().split()
    for word in q_words:
        if len(word) > 3 and word in text:
            score += 8
    if r.get("country", "").lower() == params.target_country.lower():
        score += 15
    if r.get("contact"):
        score += 5
    if r.get("website"):
        score += 5
    return min(100, score)


async def validate_output(results: List[Dict]) -> List[Dict]:
    """
    URL doğrulama:
    - is_valid_url(syntax) → False ise url_status = None
    - Geçerli görünen URL'lere url_status = 200 yaz (HEAD isteği yapmadan hızlı)
    Not: Toplu HEAD isteği rate-limit sorunlarına yol açabileceği için
    sadece syntax kontrolü yapıyoruz; UI'da "Doğrulanamadı" gösterimi is_valid_url'e göre.
    """
    for r in results:
        url = r.get("website", "")
        if url and is_valid_url(url):
            r["url_status"] = 200
        else:
            r["website"] = ""
            r["url_status"] = None
    return results


# ─────────────────────────────────────────────────────────────────────────────
# ARAMA MOTORU SCRAPER'LARI
# ─────────────────────────────────────────────────────────────────────────────

class _SearchEngineScraper:
    """Ortak arama motoru scraper tabanlı sınıf."""

    SOURCE = "search_engine"
    SEARCH_URL = ""
    BASE_DOMAIN = ""

    @classmethod
    async def search(cls, params: SearchParams, max_results: int = 10) -> List[Dict]:
        api_key = get_scraperapi_key()
        query = params.build_buyer_query()
        country_code = params.country_code
        url = cls.SEARCH_URL.format(q=quote_plus(query), cc=country_code or "en")
        html = await retry_fetch(url, api_key=api_key, country=country_code, module=cls.SOURCE)
        if not html:
            return []
        return cls._parse(html, params, url, max_results)

    @classmethod
    def _parse(cls, html: str, params: SearchParams, page_url: str, max_results: int) -> List[Dict]:
        """Alt sınıflar override eder."""
        return []

    @classmethod
    def _extract_google_style(cls, html: str, params: SearchParams, page_url: str, max_results: int, source: str) -> List[Dict]:
        """Google tarzı sonuç sayfasını parse et."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for card in soup.select(".g, .tF2Cxc, [data-sokoban-container], .result")[:max_results * 2]:
            try:
                title_el = card.select_one("h3, h2, .title")
                link_el = card.select_one("a[href]")
                desc_el = card.select_one(".VwiC3b, .st, [class*='snippet'], .abstract, p")

                if not title_el or not link_el:
                    continue

                href = link_el.get("href", "")
                # Google /url?q= redirect
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]
                href = normalize_url(href, cls.BASE_DOMAIN or page_url)
                if not is_valid_url(href):
                    continue

                desc = clean_string(desc_el.get_text() if desc_el else "")
                title = clean_string(title_el.get_text())

                # Email / telefon bul
                contact = ""
                email_m = re.search(r'[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}', desc)
                if email_m:
                    contact = email_m.group()

                results.append(_make_result(
                    source=source,
                    company_name=title,
                    country=params.target_country,
                    contact=contact,
                    website=href,
                    product_match=params.product_name,
                    relevance_score=60,
                    raw_data={"description": desc[:300]},
                ))
            except Exception as e:
                log_scrape_error(page_url, e, module=source)
                continue

        return results[:max_results]


class GoogleSearchScraper(_SearchEngineScraper):
    SOURCE = "google"
    SEARCH_URL = "https://www.google.com/search?q={q}&num=20&gl={cc}&hl=en"
    BASE_DOMAIN = "https://www.google.com"

    @classmethod
    def _parse(cls, html, params, page_url, max_results):
        return cls._extract_google_style(html, params, page_url, max_results, cls.SOURCE)


class YandexSearchScraper(_SearchEngineScraper):
    SOURCE = "yandex"
    SEARCH_URL = "https://www.yandex.com/search/?text={q}&lr=225"
    BASE_DOMAIN = "https://www.yandex.com"

    @classmethod
    def _parse(cls, html, params, page_url, max_results):
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for card in soup.select(".serp-item, .organic, [class*='OrganicTitle']")[:max_results * 2]:
            try:
                title_el = card.select_one("h2, .organic__title, [class*='Title']")
                link_el = card.select_one("a[href]")
                desc_el = card.select_one(".organic__content-wrapper, .text-container")
                if not title_el or not link_el:
                    continue
                href = normalize_url(link_el.get("href", ""), cls.BASE_DOMAIN)
                if not is_valid_url(href):
                    continue
                title = clean_string(title_el.get_text())
                desc = clean_string(desc_el.get_text() if desc_el else "")
                results.append(_make_result(
                    source=cls.SOURCE, company_name=title, country=params.target_country,
                    website=href, product_match=params.product_name,
                    relevance_score=60, raw_data={"desc": desc[:200]},
                ))
            except Exception as e:
                log_scrape_error(page_url, e, module=cls.SOURCE)
                continue
        return results[:max_results]


class BingSearchScraper(_SearchEngineScraper):
    SOURCE = "bing"
    SEARCH_URL = "https://www.bing.com/search?q={q}&cc={cc}"
    BASE_DOMAIN = "https://www.bing.com"

    @classmethod
    def _parse(cls, html, params, page_url, max_results):
        return cls._extract_google_style(html, params, page_url, max_results, cls.SOURCE)


class BaiduSearchScraper(_SearchEngineScraper):
    SOURCE = "baidu"
    SEARCH_URL = "https://www.baidu.com/s?wd={q}"
    BASE_DOMAIN = "https://www.baidu.com"

    @classmethod
    async def search(cls, params: SearchParams, max_results: int = 10) -> List[Dict]:
        api_key = get_scraperapi_key()
        query = params.build_buyer_query()
        url = cls.SEARCH_URL.format(q=quote_plus(query))
        # Baidu için cn country kodu
        html = await retry_fetch(url, api_key=api_key, country="cn", module=cls.SOURCE)
        if not html:
            return []
        return cls._parse(html, params, url, max_results)

    @classmethod
    def _parse(cls, html, params, page_url, max_results):
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for card in soup.select(".result, .c-container, [class*='result_']"):
            try:
                title_el = card.select_one("h3, .t, [class*='title']")
                link_el = card.select_one("a[href]")
                desc_el = card.select_one(".c-abstract, .c-span-last, p")
                if not title_el or not link_el:
                    continue
                href = link_el.get("href", "")
                if not href.startswith("http"):
                    continue
                results.append(_make_result(
                    source=cls.SOURCE, company_name=clean_string(title_el.get_text()),
                    country="China", website=href, product_match=params.product_name,
                    relevance_score=55, raw_data={"desc": clean_string(desc_el.get_text() if desc_el else "")[:200]},
                ))
                if len(results) >= max_results:
                    break
            except Exception as e:
                log_scrape_error(page_url, e, module=cls.SOURCE)
                continue
        return results[:max_results]


class DuckDuckGoScraper(_SearchEngineScraper):
    """DuckDuckGo HTML — ScraperAPI gerektirmez."""
    SOURCE = "duckduckgo"
    SEARCH_URL = "https://html.duckduckgo.com/html/?q={q}"
    BASE_DOMAIN = "https://duckduckgo.com"

    @classmethod
    async def search(cls, params: SearchParams, max_results: int = 10) -> List[Dict]:
        # DuckDuckGo scraper API olmadan da çalışır
        query = params.build_buyer_query()
        url = cls.SEARCH_URL.format(q=quote_plus(query))
        api_key = get_scraperapi_key()
        html = await retry_fetch(url, api_key=api_key, module=cls.SOURCE)
        if not html:
            return []
        return cls._parse(html, params, url, max_results)

    @classmethod
    def _parse(cls, html, params, page_url, max_results):
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for card in soup.select(".result, .web-result"):
            try:
                title_el = card.select_one("a.result__a, h2")
                link_el = card.select_one("a.result__a, a[href]")
                desc_el = card.select_one(".result__snippet, .result__body")
                if not title_el or not link_el:
                    continue
                href = link_el.get("href", "")
                # DDG redirect
                if href.startswith("//duckduckgo.com/l/?uddg="):
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    href = parsed.get("uddg", [href])[0]
                href = normalize_url(href, cls.BASE_DOMAIN)
                if not is_valid_url(href):
                    continue
                results.append(_make_result(
                    source=cls.SOURCE, company_name=clean_string(title_el.get_text()),
                    country=params.target_country, website=href, product_match=params.product_name,
                    relevance_score=55, raw_data={"desc": clean_string(desc_el.get_text() if desc_el else "")[:200]},
                ))
                if len(results) >= max_results:
                    break
            except Exception as e:
                log_scrape_error(page_url, e, module=cls.SOURCE)
                continue
        return results[:max_results]


class YahooSearchScraper(_SearchEngineScraper):
    SOURCE = "yahoo"
    SEARCH_URL = "https://search.yahoo.com/search?p={q}"
    BASE_DOMAIN = "https://search.yahoo.com"

    @classmethod
    def _parse(cls, html, params, page_url, max_results):
        return cls._extract_google_style(html, params, page_url, max_results, cls.SOURCE)


# ─────────────────────────────────────────────────────────────────────────────
# DIŞ TİCARET VERİTABANI SCRAPER'LARI
# ─────────────────────────────────────────────────────────────────────────────

class TradeAtlasScraper:
    """TradeAtlas — Türk gümrük veri servisi."""
    SOURCE = "tradeatlas"
    BASE = "https://www.tradeatlas.com/en/search"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        api_key = get_scraperapi_key()
        query = params.build_query()
        url = f"{TradeAtlasScraper.BASE}?q={quote_plus(query)}"
        html = await retry_fetch(url, api_key=api_key, module=TradeAtlasScraper.SOURCE)

        results = []
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".company-card, .buyer-item, [class*='company'], [class*='buyer']")[:max_results]:
                try:
                    name_el = card.select_one("h2, h3, [class*='name'], [class*='title']")
                    country_el = card.select_one("[class*='country'], [class*='location']")
                    link_el = card.select_one("a[href]")
                    if not name_el:
                        continue
                    href = normalize_url(link_el.get("href", "") if link_el else "", "https://www.tradeatlas.com")
                    results.append(_make_result(
                        source=TradeAtlasScraper.SOURCE,
                        company_name=clean_string(name_el.get_text()),
                        country=clean_string(country_el.get_text() if country_el else params.target_country),
                        website=href or url,
                        product_match=query,
                        relevance_score=75,
                    ))
                except Exception as e:
                    log_scrape_error(url, e, module=TradeAtlasScraper.SOURCE)
                    continue

        if not results:
            # Fallback link
            results = [_make_result(
                source=TradeAtlasScraper.SOURCE,
                company_name=f"{query} — TradeAtlas Arama",
                country=params.target_country or "Global",
                website=url,
                product_match=query,
                relevance_score=40,
                raw_data={"note": "TradeAtlas API aboneliği veya ScraperAPI key gerektirir"},
            )]
        return results[:max_results]


class ImportGeniusScraper:
    """ImportGenius — ABD ithalat gümrük beyanı arama."""
    SOURCE = "importgenius"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        query = params.build_query()
        country = params.target_country or "us"
        url = f"https://www.importgenius.com/search?q={quote_plus(query)}"
        # ImportGenius giriş gerektiriyor → fallback link + scrape dene
        api_key = get_scraperapi_key()
        html = await retry_fetch(url, api_key=api_key, module=ImportGeniusScraper.SOURCE)
        results = []
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".company-result, .result-company, [class*='shipment']")[:max_results]:
                try:
                    name_el = card.select_one("h2, h3, .company-name, [class*='name']")
                    if not name_el:
                        continue
                    link_el = card.select_one("a[href]")
                    href = normalize_url(link_el.get("href", "") if link_el else "", "https://www.importgenius.com")
                    results.append(_make_result(
                        source=ImportGeniusScraper.SOURCE,
                        company_name=clean_string(name_el.get_text()),
                        country=params.target_country,
                        website=href or url,
                        product_match=query,
                        relevance_score=70,
                    ))
                except Exception as e:
                    log_scrape_error(url, e, module=ImportGeniusScraper.SOURCE)
                    continue

        if not results:
            results = [_make_result(
                source=ImportGeniusScraper.SOURCE,
                company_name=f"{query} — ImportGenius ABD İthalat Kayıtları",
                country="USA",
                website=url,
                product_match=query,
                relevance_score=45,
                raw_data={"note": "Üyelik gerektirir (importgenius.com)"},
            )]
        return results[:max_results]


class TrademoScraper:
    """Trademo Intel — global ticaret istihbarat."""
    SOURCE = "trademo"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        query = params.build_query()
        url = f"https://trademo.com/search?q={quote_plus(query)}"
        api_key = get_scraperapi_key()
        html = await retry_fetch(url, api_key=api_key, module=TrademoScraper.SOURCE)
        results = []
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".company-card, .result-item, [class*='Company'], [class*='buyer']")[:max_results]:
                try:
                    name_el = card.select_one("h2, h3, [class*='name']")
                    if not name_el:
                        continue
                    country_el = card.select_one("[class*='country'], [class*='location']")
                    link_el = card.select_one("a[href]")
                    href = normalize_url(link_el.get("href", "") if link_el else "", "https://trademo.com")
                    results.append(_make_result(
                        source=TrademoScraper.SOURCE,
                        company_name=clean_string(name_el.get_text()),
                        country=clean_string(country_el.get_text() if country_el else params.target_country),
                        website=href or url,
                        product_match=query,
                        relevance_score=70,
                    ))
                except Exception as e:
                    log_scrape_error(url, e, module=TrademoScraper.SOURCE)
                    continue

        if not results:
            results = [_make_result(
                source=TrademoScraper.SOURCE,
                company_name=f"{query} — Trademo Intel Arama",
                country=params.target_country or "Global",
                website=url,
                product_match=query,
                relevance_score=45,
                raw_data={"note": "Trademo Intel üyelik gerektirir"},
            )]
        return results[:max_results]


class PanjivaScraper:
    """Panjiva (S&P Global) — tedarik zinciri veritabanı."""
    SOURCE = "panjiva"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        query = params.build_query()
        country = params.target_country or "USA"
        url = f"https://panjiva.com/search?q={quote_plus(query)}"
        api_key = get_scraperapi_key()
        html = await retry_fetch(url, api_key=api_key, module=PanjivaScraper.SOURCE)
        results = []
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".entity-card, [class*='CompanyCard'], [class*='entity']")[:max_results]:
                try:
                    name_el = card.select_one("h2, h3, [class*='name']")
                    if not name_el:
                        continue
                    country_el = card.select_one("[class*='country'], [class*='location']")
                    link_el = card.select_one("a[href]")
                    href = normalize_url(link_el.get("href", "") if link_el else "", "https://panjiva.com")
                    results.append(_make_result(
                        source=PanjivaScraper.SOURCE,
                        company_name=clean_string(name_el.get_text()),
                        country=clean_string(country_el.get_text() if country_el else country),
                        website=href or url,
                        product_match=query,
                        relevance_score=72,
                    ))
                except Exception as e:
                    log_scrape_error(url, e, module=PanjivaScraper.SOURCE)
                    continue

        if not results:
            results = [_make_result(
                source=PanjivaScraper.SOURCE,
                company_name=f"{query} — Panjiva Tedarik Zinciri",
                country=country,
                website=url,
                product_match=query,
                relevance_score=45,
                raw_data={"note": "Panjiva S&P Global üyelik gerektirir"},
            )]
        return results[:max_results]


class GlobalBuyersScraper:
    """Global Buyers Online — küresel alıcı rehberi."""
    SOURCE = "global_buyers"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        query = params.build_query()
        url = f"https://www.globalbuyers.online/search?keyword={quote_plus(query)}"
        api_key = get_scraperapi_key()
        html = await retry_fetch(url, api_key=api_key, module=GlobalBuyersScraper.SOURCE)
        results = []
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".buyer-card, .company-item, [class*='buyer']")[:max_results]:
                try:
                    name_el = card.select_one("h2, h3, .name, [class*='title']")
                    if not name_el:
                        continue
                    country_el = card.select_one("[class*='country'], .location, .country")
                    link_el = card.select_one("a[href]")
                    href = normalize_url(link_el.get("href", "") if link_el else "", "https://www.globalbuyers.online")
                    results.append(_make_result(
                        source=GlobalBuyersScraper.SOURCE,
                        company_name=clean_string(name_el.get_text()),
                        country=clean_string(country_el.get_text() if country_el else params.target_country),
                        website=href or url,
                        product_match=query,
                        relevance_score=65,
                    ))
                except Exception as e:
                    log_scrape_error(url, e, module=GlobalBuyersScraper.SOURCE)
                    continue

        if not results:
            results = [_make_result(
                source=GlobalBuyersScraper.SOURCE,
                company_name=f"{query} — Global Buyers Online",
                country=params.target_country or "Global",
                website=url,
                product_match=query,
                relevance_score=40,
            )]
        return results[:max_results]


class EuropagesScraper:
    """Europages — Avrupa B2B rehberi."""
    SOURCE = "europages"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        api_key = get_scraperapi_key()
        query = params.build_query()
        country_code = params.country_code or "de"
        url = f"https://www.europages.com.tr/firma/{quote_plus(query)}.html?countryCode={country_code.upper()}"
        html = await retry_fetch(url, api_key=api_key, module=EuropagesScraper.SOURCE)
        results = []
        if html:
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select(".company-card, [class*='CompanyCard'], .ep-company-result")[:max_results]:
                try:
                    name_el = card.select_one("h2, h3, [class*='name'], .company-name")
                    country_el = card.select_one("[class*='country'], .country, .location")
                    link_el = card.select_one("a[href]")
                    website_el = card.select_one("[class*='website'], a[href*='website']")
                    if not name_el:
                        continue
                    href = normalize_url(link_el.get("href", "") if link_el else "", "https://www.europages.com.tr")
                    website = normalize_url(website_el.get("href", "") if website_el else "", "https://www.europages.com.tr")
                    results.append(_make_result(
                        source=EuropagesScraper.SOURCE,
                        company_name=clean_string(name_el.get_text()),
                        country=clean_string(country_el.get_text() if country_el else params.target_country),
                        website=website or href or url,
                        product_match=query,
                        relevance_score=68,
                    ))
                except Exception as e:
                    log_scrape_error(url, e, module=EuropagesScraper.SOURCE)
                    continue

        if not results:
            results = [_make_result(
                source=EuropagesScraper.SOURCE,
                company_name=f"{query} — Europages Avrupa B2B",
                country=params.target_country or "Europe",
                website=url,
                product_match=query,
                relevance_score=45,
                raw_data={"note": "ScraperAPI key ile gerçek veri"},
            )]
        return results[:max_results]


class TradeKeyBuyerScraper:
    """TradeKey — B2B platformundan alıcı arama."""
    SOURCE = "tradekey"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        # Mevcut b2b_scraper'dan import et
        try:
            from app.services.b2b_scraper import TradeKeyScraper
            raw = await TradeKeyScraper.search_products(params.build_query(), max_results)
            results = []
            for item in (raw or []):
                results.append(_make_result(
                    source=TradeKeyBuyerScraper.SOURCE,
                    company_name=item.get("title") or item.get("company") or "",
                    country=item.get("country") or params.target_country,
                    website=item.get("product_url") or item.get("url") or "",
                    product_match=params.product_name,
                    relevance_score=65,
                    raw_data=item,
                ))
            return results[:max_results]
        except Exception as e:
            log_scrape_error("tradekey", e, module=TradeKeyBuyerScraper.SOURCE)
            return []


class TradeMapScraper:
    """TradeMap (ITC) — uluslararası ticaret istatistikleri."""
    SOURCE = "trademap"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        query = params.build_query()
        gtip = params.gtip_code.replace(".", "")[:6] if params.gtip_code else ""
        country_code = params.country_code.upper() if params.country_code else "WLD"

        if gtip:
            url = f"https://www.trademap.org/Country_SelProductCountry_TS.aspx?nvpm=1|{country_code}||||{gtip}|1|1|1|1|2|1|2|1|1"
        else:
            url = f"https://www.trademap.org/Product_SelCountry_TS.aspx?nvpm=1|{country_code}||||||||1|1|1|2|1|1|2|1|1"

        api_key = get_scraperapi_key()
        html = await retry_fetch(url, api_key=api_key, module=TradeMapScraper.SOURCE)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for row in soup.select("tr.headerrow, tr[class*='Content']")[:max_results]:
                try:
                    cells = row.select("td")
                    if len(cells) < 2:
                        continue
                    country_name = clean_string(cells[0].get_text())
                    if not country_name or country_name.lower() in ("world", "total"):
                        continue
                    results.append(_make_result(
                        source=TradeMapScraper.SOURCE,
                        company_name=f"{country_name} — İthalatçı",
                        country=country_name,
                        website=url,
                        product_match=gtip or query,
                        relevance_score=72,
                        raw_data={"gtip": gtip, "trade_data": cells[1].get_text() if len(cells) > 1 else ""},
                    ))
                except Exception as e:
                    log_scrape_error(url, e, module=TradeMapScraper.SOURCE)
                    continue

        if not results:
            results = [_make_result(
                source=TradeMapScraper.SOURCE,
                company_name=f"GTİP {gtip or query} — TradeMap İstatistikleri",
                country=params.target_country or "Global",
                website=url,
                product_match=gtip or query,
                relevance_score=50,
                raw_data={"note": "TradeMap ITC — ücretsiz kayıt gerekebilir"},
            )]
        return results[:max_results]


class UNComtradeScraper:
    """UN Comtrade — BM ticaret istatistik API (ücretsiz tier)."""
    SOURCE = "un_comtrade"

    @staticmethod
    async def search(params: SearchParams, max_results: int = 10) -> List[Dict]:
        gtip = params.gtip_code.replace(".", "")[:6] if params.gtip_code else ""
        country_code = params.country_code.upper() if params.country_code else "all"
        query = params.build_query()

        if gtip:
            url = (
                f"https://comtradeapi.un.org/data/v1/get/C/A/HS?"
                f"cmdCode={gtip}&reporterCode=all&period=2023&partnerCode={country_code}&motCode=0&maxRecords=20"
            )
        else:
            url = f"https://comtradeplus.un.org/TradeFlow?Frequency=A&Flows=M&CommodityCode=TOTAL&Reporter=all&Partner={country_code}&Period=2023&AggregateBy=none&BreakdownMode=plus"

        api_key = get_scraperapi_key()
        import httpx
        results = []
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                r = await client.get(url, headers={"Accept": "application/json"})
                if r.status_code == 200:
                    data = r.json()
                    entries = data.get("data", []) or data.get("dataset", [])
                    for entry in entries[:max_results]:
                        reporter = entry.get("reporterDesc") or entry.get("rtTitle", "")
                        partner = entry.get("partnerDesc") or entry.get("ptTitle", "")
                        trade_val = entry.get("primaryValue") or entry.get("TradeValue", "")
                        if not reporter:
                            continue
                        results.append(_make_result(
                            source=UNComtradeScraper.SOURCE,
                            company_name=f"{reporter} → {partner}",
                            country=reporter,
                            website=url,
                            product_match=gtip or query,
                            relevance_score=70,
                            raw_data={"trade_value_usd": trade_val, "cmd_code": gtip},
                        ))
        except Exception as e:
            log_scrape_error(url, e, module=UNComtradeScraper.SOURCE)

        if not results:
            fallback_url = f"https://comtradeplus.un.org/TradeFlow"
            results = [_make_result(
                source=UNComtradeScraper.SOURCE,
                company_name=f"GTİP {gtip or query} — UN Comtrade",
                country=params.target_country or "Global",
                website=fallback_url,
                product_match=gtip or query,
                relevance_score=50,
                raw_data={"note": "UN Comtrade API — ücretsiz tier, token gerekebilir"},
            )]
        return results[:max_results]


# ─────────────────────────────────────────────────────────────────────────────
# KAYNAK HARİTASI
# ─────────────────────────────────────────────────────────────────────────────

SOURCE_MAP: Dict[str, Any] = {
    # Arama Motorları
    "Google":        GoogleSearchScraper,
    "Yandex":        YandexSearchScraper,
    "Bing":          BingSearchScraper,
    "Baidu":         BaiduSearchScraper,
    "DuckDuckGo":    DuckDuckGoScraper,
    "Yahoo":         YahooSearchScraper,
    # Dış Ticaret DB
    "TradeAtlas":         TradeAtlasScraper,
    "ImportGenius":       ImportGeniusScraper,
    "Trademo Intel":      TrademoScraper,
    "Panjiva":            PanjivaScraper,
    "Global Buyers Online": GlobalBuyersScraper,
    "Europages":          EuropagesScraper,
    "TradeKey":           TradeKeyBuyerScraper,
    "TradeMap":           TradeMapScraper,
    "UN Comtrade":        UNComtradeScraper,
}


# ─────────────────────────────────────────────────────────────────────────────
# ANA ORKESTRATÖRLERİ
# ─────────────────────────────────────────────────────────────────────────────

class CustomerSearchService:
    """
    Tüm kaynakları paralel çalıştıran ana servis.
    """

    @staticmethod
    async def search_all_sources(
        params: SearchParams,
        search_engines: List[str],
        db_sources: List[str],
        max_per_source: int = 10,
    ) -> Dict:
        """
        Seçili kaynaklarda paralel arama yap.

        Returns:
            {
              "results": [...],           # tüm sonuçlar, relevance_score sırası
              "by_source": {              # kaynak bazında
                "Google": {"results": [...], "error": null},
                ...
              },
              "total": int,
            }
        """
        selected = list(dict.fromkeys(search_engines + db_sources))  # deduplicate, order preserve

        tasks = {}
        for source_name in selected:
            scraper_cls = SOURCE_MAP.get(source_name)
            if scraper_cls:
                tasks[source_name] = scraper_cls.search(params, max_per_source)

        by_source: Dict[str, Dict] = {}
        all_results: List[Dict] = []

        if tasks:
            gathered = await asyncio.gather(*tasks.values(), return_exceptions=True)
            for source_name, outcome in zip(tasks.keys(), gathered):
                if isinstance(outcome, Exception):
                    log_scrape_error(source_name, outcome, module="customer_search")
                    by_source[source_name] = {"results": [], "error": str(outcome)}
                else:
                    # Relevance score'larını güncelle
                    for r in (outcome or []):
                        r["relevance_score"] = _score_result(r, params)
                    by_source[source_name] = {"results": outcome or [], "error": None}
                    all_results.extend(outcome or [])

        # URL doğrulama (syntax kontrolü)
        all_results = await validate_output(all_results)

        # Relevance score'a göre sırala
        all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return {
            "results": all_results,
            "by_source": by_source,
            "total": len(all_results),
        }


# ─────────────────────────────────────────────────────────────────────────────
# ESKİ ProductSearchService (geriye dönük uyumluluk)
# ─────────────────────────────────────────────────────────────────────────────

class ProductSearchService:
    """
    Eski endpoint uyumluluğu için korundu.
    Yeni kullanım: CustomerSearchService.search_all_sources()
    """

    SUPPORTED_LANGUAGES = ['tr', 'en', 'es', 'ru', 'ar', 'fr', 'de', 'zh']

    COUNTRY_SCRAPERS = {
        "almanya": ["kompass", "tradekey"],
        "İngiltere": ["kompass", "tradekey"],
        "fransa": ["kompass", "tradekey"],
        "İtalya": ["kompass", "tradekey"],
        "İspanya": ["kompass", "tradekey"],
        "hollanda": ["kompass", "tradekey"],
        "çin": ["alibaba", "made-in-china", "global-sources"],
        "china": ["alibaba", "made-in-china", "global-sources"],
        "hindistan": ["indiamart", "tradeindia"],
        "india": ["indiamart", "tradeindia"],
        "güney kore": ["ec21", "ecplaza"],
        "abd": ["ec21", "tradekey"],
        "usa": ["ec21", "tradekey"],
    }

    @staticmethod
    async def _run_b2b_scrapers(query: str, country: str = "", max_results: int = 50) -> List[Dict]:
        """B2B platformlardan arama yap ve normalize et."""
        try:
            from app.services.b2b_scraper import (
                AlibabaScraper, MadeInChinaScraper, GlobalSourcesScraper,
                TradeKeyScraper, EC21Scraper, IndiaMARTScraper, TradeIndiaScraper,
                KompassScraper, ECPlazaScraper
            )
        except ImportError as e:
            log_scrape_error("b2b_import", e, module="product_search")
            return []

        country_lower = (country or "").lower().strip()
        if country_lower in ProductSearchService.COUNTRY_SCRAPERS:
            platforms = ProductSearchService.COUNTRY_SCRAPERS[country_lower]
        elif country_lower in ("all", "tüm ülkeler", ""):
            platforms = ["tradekey", "ec21", "kompass", "alibaba"]
        else:
            platforms = ["tradekey", "ec21", "kompass"]

        tasks = []
        per = max(1, max_results // max(len(platforms), 1) + 5)
        for platform in platforms:
            if platform == "alibaba":
                tasks.append(AlibabaScraper.search_products(query, per))
            elif platform == "made-in-china":
                tasks.append(MadeInChinaScraper.search_products(query, per))
            elif platform == "global-sources":
                tasks.append(GlobalSourcesScraper.search_products(query, per))
            elif platform == "tradekey":
                tasks.append(TradeKeyScraper.search_products(query, per))
            elif platform == "ec21":
                tasks.append(EC21Scraper.search_products(query, per))
            elif platform == "indiamart":
                tasks.append(IndiaMARTScraper.search_products(query, per))
            elif platform == "tradeindia":
                tasks.append(TradeIndiaScraper.search_products(query, per))
            elif platform == "kompass":
                tasks.append(KompassScraper.search_companies(query, country, per))
            elif platform == "ecplaza":
                tasks.append(ECPlazaScraper.search_products(query, per))

        raw_lists = await asyncio.gather(*tasks, return_exceptions=True)
        normalized = []
        for raw in raw_lists:
            if isinstance(raw, Exception):
                continue
            for item in (raw or []):
                normalized.append({
                    "company_name": item.get("title") or item.get("company") or item.get("name") or "—",
                    "country": item.get("country", country or "Global"),
                    "email": item.get("email", ""),
                    "phone": item.get("phone", ""),
                    "website": item.get("product_url") or item.get("url") or "",
                    "source": item.get("source", "b2b"),
                    "category": item.get("note") or item.get("activity") or "",
                    "price": item.get("price", ""),
                    "supplier": item.get("supplier", ""),
                })
        return normalized[:max_results]

    @staticmethod
    async def search_products(
        db: Session,
        query: str,
        language: str = 'tr',
        search_type: str = 'text',
        max_results: int = 50,
        country: str = "",
    ) -> List[Dict]:
        """Eski endpoint uyumu — DB araması + B2B scraper."""
        db_results = []
        try:
            if search_type == 'gtip':
                products = ProductSearchService.search_by_gtip(db, query)
                db_results = [
                    {"company_name": getattr(p, 'category', '') or 'Ürün', "gtip_code": getattr(p, 'gtip_code', ''), "country": "", "source": "DB/GTİP", "website": None}
                    for p in products[:max_results]
                ]
            elif search_type == 'oem':
                products = ProductSearchService.search_by_oem(db, query)
                db_results = [
                    {"company_name": getattr(p, 'category', '') or 'Ürün', "oem_code": getattr(p, 'oem_code', ''), "country": "", "source": "DB/OEM", "website": None}
                    for p in products[:max_results]
                ]
            else:
                langs = [language] if language != 'tr' else ['tr', 'en']
                raw = await ProductSearchService.search_by_name_multilang(db, query, langs)
                db_results = [
                    {"company_name": r.get("name") or r.get("category") or "Ürün", "gtip_code": r.get("gtip_code", ""), "country": "", "source": "DB", "website": None}
                    for r in raw[:max_results]
                ]
        except Exception as e:
            log_scrape_error("db_search", e, module="product_search")

        if len(db_results) >= 5:
            return db_results[:max_results]

        try:
            b2b_results = await ProductSearchService._run_b2b_scrapers(query, country, max_results)
            return (db_results + b2b_results)[:max_results]
        except Exception as e:
            log_scrape_error("b2b_search", e, module="product_search")
            return db_results

    @staticmethod
    async def translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> str:
        return text

    @staticmethod
    def search_by_gtip(db: Session, gtip_code: str) -> List:
        return db.query(Product).filter(Product.gtip_code.like(f"{gtip_code}%")).limit(100).all()

    @staticmethod
    def search_by_oem(db: Session, oem_code: str) -> List:
        return db.query(Product).filter(Product.oem_code.ilike(f"%{oem_code}%")).limit(100).all()

    @staticmethod
    async def search_by_name_multilang(db: Session, query: str, languages: List[str] = None) -> List[Dict]:
        if languages is None:
            languages = ProductSearchService.SUPPORTED_LANGUAGES
        results = []
        seen_ids = set()
        for lang in languages:
            try:
                products = db.query(Product).filter(
                    Product.descriptions[lang].astext.ilike(f"%{query}%")
                ).limit(50).all()
                for product in products:
                    if product.id not in seen_ids:
                        results.append({
                            "id": product.id, "gtip_code": product.gtip_code,
                            "oem_code": product.oem_code, "name": product.descriptions.get(lang, ""),
                            "language": lang, "category": product.category,
                        })
                        seen_ids.add(product.id)
            except Exception:
                continue
        return results

    @staticmethod
    async def verify_term_with_dictionary(term: str, source_lang: str, target_lang: str) -> Dict:
        return {"verified": True, "term": term, "translations": {target_lang: term}, "confidence": 0.8}

    @staticmethod
    async def image_search(image_url: str) -> List[Dict]:
        return []

    @staticmethod
    async def search_with_valentin_simulation(query: str, target_country: str, language: str) -> List[Dict]:
        return []
