from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.contact_finder import ContactFinderService, search_companies_by_keyword
from app.services.activity_logger import log_activity_safe, Module

router = APIRouter()


class ContactFinderRequest(BaseModel):
    websites: List[str]
    positions: Optional[List[str]] = None


class BulkSearchRequest(BaseModel):
    keyword: str
    country: Optional[str] = ""
    find_contacts: bool = False


@router.post("/find")
async def find_contacts(
    request: ContactFinderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Web sitelerinden e-posta, telefon ve sosyal medya bilgisi çıkar.
    
    - Her web sitesi için ana sayfa + iletişim sayfası taranır.
    - E-postalar, telefon numaraları, LinkedIn/Twitter/Facebook profilleri bulunur.
    - ScraperAPI key girilirse başarı oranı artar.
    """
    if not request.websites:
        raise HTTPException(status_code=400, detail="En az bir web sitesi girin")

    # Kredi kontrolü (isteğe bağlı — şimdilik kapalı)
    # credits_needed = len(request.websites)
    # if current_user.query_credits < credits_needed:
    #     raise HTTPException(status_code=403, detail=f"Yetersiz kredi")

    results = await ContactFinderService.find_contacts_bulk(request.websites)

    total_emails = sum(len(r.get("emails", [])) for r in results)
    total_phones = sum(len(r.get("phones", [])) for r in results)

    log_activity_safe(
        db, current_user.id,
        module=Module.CONTACT,
        action=f"{len(request.websites)} web sitesinden iletişim bilgisi arandı",
        credits_used=len(request.websites),
        status="success",
        meta_data={"websites_count": len(request.websites), "emails_found": total_emails, "phones_found": total_phones}
    )

    return {
        "results": results,
        "total_websites_scanned": len(results),
        "total_emails_found": total_emails,
        "total_phones_found": total_phones,
        "tip": "ScraperAPI key eklenirse daha fazla site taranabilir (Dashboard → Ayarlar → Scraping)"
    }


@router.post("/find-single")
async def find_contacts_single(
    url: str,
    current_user: User = Depends(get_current_active_user)
):
    """Tek bir web sitesinden iletişim bilgisi çıkar"""
    result = await ContactFinderService.find_contacts(url)
    return result


@router.post("/verify-email")
async def verify_email_address(
    email: str,
    current_user: User = Depends(get_current_active_user)
):
    """E-posta adresini doğrula (format + domain kontrolü)"""
    result = ContactFinderService.verify_email(email)
    return result


@router.post("/search-companies")
async def search_companies(
    request: BulkSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Google'da şirket ara ve iletişim bilgilerini topla.
    
    - ScraperAPI key gerekli (Dashboard → Ayarlar → Scraping)
    - Keyword + ülke ile şirket web siteleri bulunur
    - Opsiyonel: her şirketi iletişim bilgisi de taranir
    """
    companies = await search_companies_by_keyword(request.keyword, request.country)

    if request.find_contacts and companies:
        urls = [c["url"] for c in companies if c.get("url")]
        contact_results = await ContactFinderService.find_contacts_bulk(urls[:10])
        # Merge
        for i, company in enumerate(companies):
            if i < len(contact_results):
                company["contacts"] = contact_results[i]

    log_activity_safe(
        db, current_user.id,
        module=Module.CONTACT,
        action=f"Şirket araması: {request.keyword[:80]}",
        credits_used=2,
        status="success",
        meta_data={"keyword": request.keyword, "country": request.country, "companies_found": len(companies), "find_contacts": request.find_contacts}
    )

    return {
        "keyword": request.keyword,
        "country": request.country,
        "companies_found": len(companies),
        "results": companies
    }


@router.post("/upload-excel")
async def upload_website_list(
    current_user: User = Depends(get_current_active_user)
):
    """Excel yükleme — yakında eklenecek"""
    return {
        "message": "Excel yükleme özelliği yakında eklenecek",
        "status": "pending"
    }
