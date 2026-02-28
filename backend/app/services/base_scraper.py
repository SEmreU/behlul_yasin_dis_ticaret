"""
BaseScraper — Tüm scraper'lar için ortak yardımcı sınıf.

Metodlar:
  normalize_url(href, base)  → urljoin ile mutlak URL üret
  validate_url(url)          → HEAD ile 200-299 kontrolü (async)
  retry_request(url, ...)    → 3 deneme, exponential backoff
  log_error(...)             → json-line formatında log
  clean_string(text)         → strip + HTML entity decode + kontrol karakterlerini temizle
"""

import asyncio
import html as html_lib
import logging
import os
import time
import unicodedata
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse, quote_plus

import httpx

logger = logging.getLogger("scraper")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ─── Ortak API Key okuma ───────────────────────────────────────────────────────

def get_scraperapi_key() -> str:
    """DB önce, sonra env'den ScraperAPI key al."""
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


def build_scraperapi_url(url: str, api_key: str, render: bool = False, country: str = "") -> str:
    """ScraperAPI proxy URL oluştur."""
    proxy = f"http://api.scraperapi.com/?api_key={api_key}&url={quote_plus(url)}"
    if render:
        proxy += "&render=true"
    if country:
        proxy += f"&country_code={country}"
    return proxy


# ─── URL Yardımcıları ─────────────────────────────────────────────────────────

def normalize_url(href: str, base: str = "") -> str:
    """
    urljoin kullanarak mutlak URL üret.
    - Protocol-relative URL'leri düzelt (//example.com → https://example.com)
    - Relative URL'leri base_url ile birleştir
    - Fragment (#...) kısımlarını temizle
    """
    if not href:
        return ""

    href = href.strip()

    # Protocol-relative
    if href.startswith("//"):
        href = "https:" + href

    # Mutlak URL ise direkt dön (fragment'ı temizle)
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        clean = parsed._replace(fragment="").geturl()
        return clean

    # Relative URL — base gerekli
    if base:
        return urljoin(base, href)

    return href


def is_valid_url(url: str) -> bool:
    """URL syntax geçerliliğini kontrol et (sync, HTTP isteği yapmaz)."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


# ─── String Temizleme ─────────────────────────────────────────────────────────

def clean_string(text: str, max_len: int = 500) -> str:
    """
    - HTML entity decode (&amp; → & vb.)
    - Görünmez/kontrol karakterlerini temizle
    - Çoklu boşlukları tek boşluğa indir
    - strip + max_len
    """
    if not text:
        return ""
    # HTML entities
    text = html_lib.unescape(text)
    # Kontrol karakterlerini kaldır (null bytes, zero-width spaces vb.)
    text = "".join(
        c for c in text
        if unicodedata.category(c) not in ("Cc", "Cf") or c in ("\n", "\t", " ")
    )
    # Çoklu boşluk
    text = " ".join(text.split())
    return text[:max_len].strip()


# ─── Hata Loglama ─────────────────────────────────────────────────────────────

def log_scrape_error(url: str, error: Exception, attempt: int = 1, module: str = "scraper") -> None:
    """Scraper hatalarını logla."""
    logger.warning(
        "[%s] ERROR url=%s attempt=%d type=%s msg=%s",
        module, url, attempt, type(error).__name__, str(error)[:200]
    )


def log_scrape_info(url: str, status: int, module: str = "scraper") -> None:
    logger.info("[%s] %s → HTTP %d", module, url, status)


# ─── Retry ile HTTP İstek ─────────────────────────────────────────────────────

async def retry_fetch(
    url: str,
    api_key: str = "",
    render: bool = False,
    country: str = "",
    max_retries: int = 3,
    timeout: int = 30,
    module: str = "scraper",
) -> Optional[str]:
    """
    URL'den HTML çek; ScraperAPI üzerinden veya doğrudan.
    - 3 deneme, 1s/2s/4s exponential backoff
    - Rate-limit (429) gelirse 60s bekle
    - Hataları logla
    """
    target = build_scraperapi_url(url, api_key, render, country) if api_key else url

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers=COMMON_HEADERS,
            ) as client:
                r = await client.get(target)

                if r.status_code == 200:
                    log_scrape_info(url, 200, module)
                    return r.text

                if r.status_code == 429:
                    logger.warning("[%s] Rate-limited (429), 60s bekleniyor...", module)
                    await asyncio.sleep(60)
                    continue

                log_scrape_info(url, r.status_code, module)
                # 4xx (404 vb.) → retry etme
                if 400 <= r.status_code < 500:
                    return None

        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as e:
            log_scrape_error(url, e, attempt, module)
        except Exception as e:
            log_scrape_error(url, e, attempt, module)

        if attempt < max_retries:
            wait = 2 ** (attempt - 1)  # 1s, 2s, 4s
            logger.info("[%s] Retry %d/%d, %ds sonra...", module, attempt, max_retries, wait)
            await asyncio.sleep(wait)

    return None


# ─── URL Doğrulama (HEAD isteği) ─────────────────────────────────────────────

async def validate_url_async(url: str, timeout: int = 8) -> bool:
    """
    HEAD isteğiyle URL'nin gerçekten erişilebilir olup olmadığını kontrol et.
    200-299 arası → True, aksi → False
    """
    if not is_valid_url(url):
        return False
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            r = await client.head(url, headers=COMMON_HEADERS)
            return 200 <= r.status_code < 300
    except Exception:
        return False


def try_selectors(soup, selectors: list):
    """
    CSS selector listesini sırayla dener; ilk None olmayan eleman döner.
    Hiçbiri bulunamazsa None döner.
    """
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            logger.debug("try_selectors hit: %s", sel)
            return el
    return None


def safe_url(href: str, base: str = "") -> str | None:
    """
    URL güvenlik zinciri:
    1. None veya boş → None
    2. '#' veya 'javascript:' ile başlıyor → None
    3. Protocol-relative veya relative → normalize_url ile absolute yap
    4. Geçerli http/https değil → None
    Geçerliyse temizlenmiş absolute URL, değilse None döner.
    """
    if not href:
        return None
    href = href.strip()
    if href.startswith("#") or href.lower().startswith("javascript:"):
        return None
    result = normalize_url(href, base)
    if not is_valid_url(result):
        return None
    return result


# ─── BaseScraper Sınıfı ────────────────────────────────────────────────────────

class BaseScraper:
    """
    Tüm scraper'ların türetileceği temel sınıf.
    Statik metodlar olarak yardımcı işlevleri sağlar.
    """

    MODULE = "base_scraper"

    @classmethod
    def normalize_url(cls, href: str, base: str = "") -> str:
        return normalize_url(href, base)

    @classmethod
    async def validate_url(cls, url: str) -> bool:
        return await validate_url_async(url)

    @classmethod
    async def retry_request(
        cls,
        url: str,
        api_key: str = "",
        render: bool = False,
        country: str = "",
        max_retries: int = 3,
    ) -> Optional[str]:
        return await retry_fetch(url, api_key, render, country, max_retries, module=cls.MODULE)

    @classmethod
    def log_error(cls, url: str, error: Exception, attempt: int = 1) -> None:
        log_scrape_error(url, error, attempt, cls.MODULE)

    @classmethod
    def clean_string(cls, text: str, max_len: int = 500) -> str:
        return clean_string(text, max_len)

    @classmethod
    def normalize_product_url(cls, href: str, base_domain: str, page_url: str) -> str:
        """
        Ürün URL'sini normalize et:
        1. Protocol-relative → https
        2. Relative → base_domain + href
        3. Mutlak → direkt
        Fragment temizle.
        """
        if not href:
            return page_url

        href = href.strip()

        # Protocol-relative
        if href.startswith("//"):
            return "https:" + href

        # Tam URL
        if href.startswith("http://") or href.startswith("https://"):
            parsed = urlparse(href)
            return parsed._replace(fragment="").geturl()

        # Relative
        return urljoin(base_domain, href)
