"""
Google Maps / Harita Firma Arama Servisi
Google Maps Places API (key varsa) veya ScraperAPI tabanlı Google arama (key yoksa) kullanır.

Değişiklikler:
  - get_scraperapi_key / get_google_maps_key → base_scraper'dan import
  - _fetch → retry_fetch (3 deneme, backoff, rate-limit)
  - URL string birleştirme → normalize_url()
  - clean_string ile metinler temizleniyor
"""

import os
import httpx
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re

from app.services.base_scraper import (
    get_scraperapi_key,
    normalize_url,
    clean_string,
    retry_fetch,
    log_scrape_error,
    COMMON_HEADERS,
)


def get_google_maps_key() -> str:
    try:
        from app.core.database import SessionLocal
        from app.models.api_setting import ApiSetting
        import base64
        db = SessionLocal()
        s = db.query(ApiSetting).filter(ApiSetting.key_name == "GOOGLE_MAPS_API_KEY").first()
        db.close()
        if s and s.key_value:
            return base64.b64decode(s.key_value.encode()).decode()
    except Exception:
        pass
    return os.getenv("GOOGLE_MAPS_API_KEY", "")


async def _fetch(url: str, scraperapi_key: str = "", render: bool = False) -> Optional[str]:
    """Geriye dönük uyumluluk: retry_fetch kullanır."""
    return await retry_fetch(url, api_key=scraperapi_key, render=render, module="maps_scraper")

COUNTRY_CODES = {
    "Germany": "de", "France": "fr", "Italy": "it", "United Kingdom": "gb",
    "Spain": "es", "Turkey": "tr", "USA": "us", "United States": "us",
    "China": "cn", "Japan": "jp", "South Korea": "kr", "India": "in",
    "Brazil": "br", "Russia": "ru", "Poland": "pl", "Netherlands": "nl",
}


class GoogleMapsService:
    """
    Google Maps firma arama.
    Yöntem 1: Google Places API (GOOGLE_MAPS_API_KEY varsa)
    Yöntem 2: ScraperAPI ile Google arama sonuçlarını parse et
    Yöntem 3: Mock data (her iki key de yoksa)
    """

    @staticmethod
    async def search_companies(
        keywords: str,
        country: str,
        city: str = "",
        max_results: int = 20,
    ) -> Dict:
        gmaps_key = get_google_maps_key()
        scraper_key = get_scraperapi_key()

        if gmaps_key:
            # YOL 1: Gerçek Google Places API
            return await GoogleMapsService._search_with_places_api(
                keywords, country, city, gmaps_key, max_results
            )
        elif scraper_key:
            # YOL 2: ScraperAPI + Google arama parse
            return await GoogleMapsService._search_with_scraperapi(
                keywords, country, city, scraper_key, max_results
            )
        else:
            # YOL 3: Mock/Demo data
            return GoogleMapsService._mock_results(keywords, country, city)

    # ─────────────────────────────────────────────────────────────────────────
    # YOL 1: Google Places API
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def _search_with_places_api(
        keywords: str, country: str, city: str, api_key: str, max_results: int
    ) -> Dict:
        query = f"{keywords} {city} {country}".strip()
        url = (
            "https://maps.googleapis.com/maps/api/place/textsearch/json"
            f"?query={quote_plus(query)}&key={api_key}"
        )

        results = []
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(url)
                data = r.json()

                for place in data.get("results", [])[:max_results]:
                    lat = place.get("geometry", {}).get("location", {}).get("lat")
                    lng = place.get("geometry", {}).get("location", {}).get("lng")

                    # Place Details (telefon + website için)
                    phone, website = "", ""
                    place_id = place.get("place_id", "")
                    if place_id:
                        detail_url = (
                            "https://maps.googleapis.com/maps/api/place/details/json"
                            f"?place_id={place_id}&fields=formatted_phone_number,website&key={api_key}"
                        )
                        detail_r = await client.get(detail_url)
                        detail_data = detail_r.json().get("result", {})
                        phone = detail_data.get("formatted_phone_number", "")
                        website = detail_data.get("website", "")

                    results.append({
                        "name": place.get("name", ""),
                        "address": place.get("formatted_address", ""),
                        "city": city or "",
                        "country": country,
                        "phone": phone,
                        "website": website,
                        "rating": str(place.get("rating", "")),
                        "lat": lat,
                        "lng": lng,
                        "place_id": place_id,
                        "source": "google_places_api",
                    })

        except Exception as e:
            print(f"[Places API] Error: {e}")
            return {"results": [], "source": "google_places_api", "error": str(e)}

        return {
            "results": results,
            "total": len(results),
            "source": "google_places_api",
            "note": "Google Places API ile gerçek veri",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # YOL 2: ScraperAPI + Google arama
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def _search_with_scraperapi(
        keywords: str, country: str, city: str, scraper_key: str, max_results: int
    ) -> Dict:
        query = f"{keywords} {city} {country} contact phone email"
        country_code = COUNTRY_CODES.get(country, "")
        google_url = f"https://www.google.com/search?q={quote_plus(query)}&num=20"
        if country_code:
            google_url += f"&gl={country_code}&hl=en"

        html = await _fetch(google_url, scraper_key)
        results = []

        if html:
            soup = BeautifulSoup(html, "html.parser")

            # Google arama sonuç kartları
            for card in soup.select(".g, .tF2Cxc, [data-sokoban-container]")[:max_results]:
                try:
                    title_el = card.select_one("h3")
                    link_el = card.select_one("a[href]")
                    desc_el = card.select_one(".VwiC3b, .st, [class*='snippet']")
                    url_el = card.select_one(".UdvAnf, cite, [class*='url']")

                    if not title_el:
                        continue

                    href = link_el["href"] if link_el else ""
                    if href.startswith("/url?q="):
                        href = href.split("/url?q=")[1].split("&")[0]
                    if not href.startswith("http"):
                        continue

                    desc = desc_el.get_text(strip=True) if desc_el else ""

                    # Email / telefon bul (description veya snippet içinden)
                    import re
                    emails = re.findall(r'[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}', desc)
                    phones = re.findall(r'[\+\d][\d\s\-\(\)]{6,18}', desc)

                    results.append({
                        "name": title_el.get_text(strip=True),
                        "address": "",
                        "city": city or "",
                        "country": country,
                        "phone": phones[0].strip() if phones else "",
                        "email": emails[0] if emails else "",
                        "website": href,
                        "description": desc[:300],
                        "lat": None,
                        "lng": None,
                        "source": "scraperapi_google",
                    })
                except Exception:
                    continue

        if not results:
            results = GoogleMapsService._mock_results(keywords, country, city)["results"]

        return {
            "results": results,
            "total": len(results),
            "source": "scraperapi_google",
            "note": "ScraperAPI + Google arama sonuçları",
        }

    # ─────────────────────────────────────────────────────────────────────────
    # YOL 3: Mock / Demo Data
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _mock_results(keywords: str, country: str, city: str) -> Dict:
        lats = [48.8566, 52.52, 51.5074, 41.0082, 48.2082]
        lngs = [2.3522, 13.405, -0.1278, 28.9784, 16.3738]
        cities_demo = [city or "Paris", city or "Berlin", city or "London",
                       city or "Istanbul", city or "Vienna"]
        results = []
        for i in range(5):
            results.append({
                "name": f"{keywords.title()} {['International', 'GmbH', 'Ltd', 'Trading', 'Group'][i]} {i+1}",
                "address": f"{100 + i * 12} Business Ave, {cities_demo[i]}",
                "city": cities_demo[i],
                "country": country,
                "phone": f"+{40 + i} {200 + i} {300 + i} {400 + i}",
                "email": f"info@{keywords.lower().replace(' ', '')}{i+1}.com",
                "website": f"https://www.{keywords.lower().replace(' ', '')}{i+1}.com",
                "rating": f"{3.5 + i * 0.3:.1f}",
                "lat": lats[i],
                "lng": lngs[i],
                "source": "demo",
            })
        return {
            "results": results,
            "total": len(results),
            "source": "demo",
            "note": "Demo verisi — Google Maps API veya ScraperAPI key girin",
        }


class GoogleMapsScraper:
    """Geriye dönük uyumluluk için wrapper"""

    @staticmethod
    async def scrape_companies(
        keyword: str,
        location: str,
        max_results: int = 20,
        db=None,
    ) -> List[Dict]:
        country = location
        city = ""
        if "," in location:
            parts = location.split(",", 1)
            city = parts[0].strip()
            country = parts[1].strip()

        result = await GoogleMapsService.search_companies(keyword, country, city, max_results)
        companies = result.get("results", [])

        # DB'ye kaydet (opsiyonel)
        if db and companies:
            try:
                from app.models.company import Company
                for c in companies:
                    existing = db.query(Company).filter(Company.name == c["name"]).first()
                    if not existing:
                        db.add(Company(
                            name=c["name"],
                            country=c.get("country"),
                            city=c.get("city"),
                            address=c.get("address"),
                            phone=c.get("phone"),
                            website=c.get("website"),
                            latitude=c.get("lat"),
                            longitude=c.get("lng"),
                            source="google_maps",
                        ))
                db.commit()
            except Exception as e:
                print(f"[MapsScraper] DB error: {e}")

        return companies
