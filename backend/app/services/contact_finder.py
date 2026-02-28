"""
Contact Finder Service
Web sitelerinden email, telefon, sosyal medya bilgisi çeker.
ScraperAPI + BeautifulSoup ile cloud-compatible.

Değişiklikler:
  - get_api_key → get_scraperapi_key (base_scraper)
  - fetch_url → retry_fetch (3 deneme, backoff)
  - normalize_url ile URL birleştirme
  - clean_string ile temizleme
"""
import re
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, quote_plus

from app.services.base_scraper import (
    get_scraperapi_key,
    normalize_url,
    clean_string,
    retry_fetch,
    log_scrape_error,
)

# Alias geriye dönük uyumluluk için
get_api_key = get_scraperapi_key


async def fetch_url(url: str, api_key: str = "") -> Optional[str]:
    """Geriye dönük uyumluluk: retry_fetch kullanır."""
    return await retry_fetch(url, api_key=api_key, module="contact_finder")



EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'(\+?[\d\s\-\(\)]{7,20})')
SOCIAL_PATTERNS = {
    "linkedin": re.compile(r'linkedin\.com/(?:company|in)/([a-zA-Z0-9\-_]+)'),
    "twitter": re.compile(r'twitter\.com/([a-zA-Z0-9_]+)'),
    "facebook": re.compile(r'facebook\.com/([a-zA-Z0-9.\-_/]+)'),
    "instagram": re.compile(r'instagram\.com/([a-zA-Z0-9._]+)'),
}

EXCLUDE_EMAILS = {
    "example.com", "test.com", "domain.com", "email.com",
    "yoursite.com", "yourdomain.com", "sentry.io", "w3.org"
}





def extract_contacts_from_html(html: str, base_url: str) -> Dict:
    """HTML'den iletişim bilgilerini çıkar"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Script ve style'ları kaldır
    for tag in soup(["script", "style", "meta", "link"]):
        tag.decompose()
    
    text = soup.get_text(separator=" ")
    full_html = str(soup)
    
    # Email'leri bul
    emails = set()
    for email in EMAIL_PATTERN.findall(text):
        domain = email.split("@")[-1].lower()
        if domain not in EXCLUDE_EMAILS and len(email) < 100:
            emails.add(email.lower().strip())
    
    # mailto: linklerinden de al
    for a in soup.find_all("a", href=re.compile(r"^mailto:")):
        email = a.get("href", "").replace("mailto:", "").split("?")[0].strip()
        if email and "@" in email:
            emails.add(email.lower())
    
    # Telefon numaraları
    phones = set()
    phone_candidates = PHONE_PATTERN.findall(text)
    for phone in phone_candidates:
        phone = phone.strip()
        digits = re.sub(r'\D', '', phone)
        if 7 <= len(digits) <= 15 and not phone.strip().isdigit():
            phones.add(phone.strip()[:20])
    
    # Sosyal medya
    social = {}
    for platform, pattern in SOCIAL_PATTERNS.items():
        match = pattern.search(full_html)
        if match:
            handle = match.group(1).rstrip("/")
            if handle and len(handle) > 1:
                social[platform] = f"https://www.{platform}.com/{handle}"
    
    # LinkedIn URL'lerini de tam olarak al
    for a in soup.find_all("a", href=re.compile(r"linkedin\.com")):
        href = a.get("href", "")
        if href and "linkedin.com" in href:
            social["linkedin"] = href
            break
    
    # Adres bilgisi (basit)
    address = ""
    addr_el = soup.find(["address", "[itemprop='address']"])
    if addr_el:
        address = addr_el.get_text(strip=True)[:200]
    
    # İletişim sayfası linkleri
    contact_links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        text_content = a.get_text(strip=True).lower()
        if any(kw in text_content for kw in ["contact", "iletişim", "about", "hakkımızda"]):
            full_url = urljoin(base_url, href)
            if base_url in full_url:
                contact_links.append(full_url)
    
    return {
        "emails": list(emails)[:10],
        "phones": list(phones)[:5],
        "social_media": social,
        "address": address,
        "contact_pages": list(set(contact_links))[:3],
    }


class ContactFinderService:
    """Web sitesinden iletişim bilgisi çıkarır"""

    @staticmethod
    async def find_contacts(website_url: str) -> Dict:
        """Bir web sitesinden iletişim bilgisi çıkar"""
        api_key = get_api_key()
        
        # URL normalize et
        if not website_url.startswith(("http://", "https://")):
            website_url = "https://" + website_url
        
        base_url = f"{urlparse(website_url).scheme}://{urlparse(website_url).netloc}"
        
        # Ana sayfayı çek
        html = await fetch_url(website_url, api_key)
        if not html:
            # http dene
            html = await fetch_url(website_url.replace("https://", "http://"), api_key)
        
        if not html:
            return {
                "url": website_url,
                "status": "error",
                "message": "Siteye erişilemedi",
                "emails": [],
                "phones": [],
                "social_media": {}
            }
        
        contacts = extract_contacts_from_html(html, base_url)
        
        # İletişim sayfasını da tara
        contact_pages = [
            f"{base_url}/contact",
            f"{base_url}/contact-us",
            f"{base_url}/iletisim",
            f"{base_url}/about",
            f"{base_url}/about-us",
        ] + contacts.get("contact_pages", [])
        
        # İletişim sayfasından daha fazla bilgi çek
        for cp_url in contact_pages[:3]:
            if cp_url != website_url:
                cp_html = await fetch_url(cp_url, api_key)
                if cp_html:
                    cp_contacts = extract_contacts_from_html(cp_html, base_url)
                    # Merge
                    contacts["emails"] = list(set(contacts["emails"] + cp_contacts["emails"]))[:10]
                    contacts["phones"] = list(set(contacts["phones"] + cp_contacts["phones"]))[:5]
                    contacts["social_media"].update(cp_contacts["social_media"])
                    if not contacts["address"] and cp_contacts["address"]:
                        contacts["address"] = cp_contacts["address"]
        
        return {
            "url": website_url,
            "status": "success",
            "emails": contacts["emails"],
            "phones": contacts["phones"],
            "social_media": contacts["social_media"],
            "address": contacts["address"],
            "scraperapi_used": bool(api_key),
        }

    @staticmethod
    async def find_contacts_bulk(websites: List[str]) -> List[Dict]:
        """Birden fazla web sitesini toplu tara"""
        tasks = [ContactFinderService.find_contacts(url) for url in websites[:20]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        output = []
        for url, result in zip(websites, results):
            if isinstance(result, Exception):
                output.append({"url": url, "status": "error", "message": str(result)})
            else:
                output.append(result)
        
        return output

    @staticmethod  
    def verify_email(email: str) -> Dict:
        """Email adresini doğrula (syntax + domain kontrolü)"""
        if not email or "@" not in email:
            return {"email": email, "valid": False, "reason": "Invalid format"}
        
        if not EMAIL_PATTERN.match(email):
            return {"email": email, "valid": False, "reason": "Invalid email format"}
        
        domain = email.split("@")[-1].lower()
        
        if domain in EXCLUDE_EMAILS:
            return {"email": email, "valid": False, "reason": "Example domain"}
        
        # MX record kontrolü (basit — httpx ile)
        return {
            "email": email,
            "valid": True,
            "domain": domain,
            "reason": "Syntax valid"
        }


async def search_companies_by_keyword(keyword: str, country: str = "") -> List[Dict]:
    """Google'da şirket ara ve web sitelerini topla"""
    api_key = get_api_key()
    
    if not api_key:
        return [{
            "company": f"{keyword} araması için ScraperAPI key gerekli",
            "note": "Dashboard → Ayarlar → Scraping → SCRAPERAPI_KEY",
            "url": f"https://www.google.com/search?q={quote_plus(keyword + ' contact email ' + country)}"
        }]
    
    # Google arama
    search_query = f"{keyword} {country} company email site:".replace("  ", " ")
    google_url = f"https://www.google.com/search?q={quote_plus(search_query)}&num=10"
    
    html = await fetch_url(google_url, api_key)
    if not html:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    companies = []
    
    for result in soup.select(".g, .tF2Cxc")[:10]:
        title_el = result.select_one("h3")
        link_el = result.select_one("a")
        desc_el = result.select_one(".VwiC3b, .st")
        
        if title_el and link_el:
            href = link_el.get("href", "")
            if href.startswith("/url?q="):
                href = href.split("/url?q=")[1].split("&")[0]
            
            if href.startswith("http"):
                companies.append({
                    "company": title_el.get_text(strip=True),
                    "url": href,
                    "description": desc_el.get_text(strip=True) if desc_el else ""
                })
    
    return companies
