"""
Fuar Analizi Endpoint'leri
Gerçek fuar verileri + Groq AI ile eşleştirme
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
import httpx
import asyncio
import os
from urllib.parse import quote_plus

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.contact_finder import ContactFinderService

router = APIRouter()


def get_groq_key() -> str:
    try:
        from app.core.database import SessionLocal
        from app.models.api_setting import ApiSetting
        import base64
        db = SessionLocal()
        setting = db.query(ApiSetting).filter(ApiSetting.key_name == "GROQ_API_KEY").first()
        db.close()
        if setting and setting.key_value:
            return base64.b64decode(setting.key_value.encode()).decode()
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")


def get_scraper_key() -> str:
    try:
        from app.core.database import SessionLocal
        from app.models.api_setting import ApiSetting
        import base64
        db = SessionLocal()
        setting = db.query(ApiSetting).filter(ApiSetting.key_name == "SCRAPERAPI_KEY").first()
        db.close()
        if setting and setting.key_value:
            return base64.b64decode(setting.key_value.encode()).decode()
    except Exception:
        pass
    return os.getenv("SCRAPERAPI_KEY", "")


# Gerçek fuar veritabanı — en büyük uluslararası fuarlar
GLOBAL_FAIRS = [
    {
        "id": 1, "name": "Automechanika Frankfurt",
        "location": "Frankfurt, Germany", "country": "Germany",
        "date": "2026-09-10", "end_date": "2026-09-14",
        "sector": ["Automotive", "Auto Parts", "Car Accessories"],
        "website": "https://automechanika.messefrankfurt.com",
        "exhibitors_count": 5000, "visitors_count": 130000,
        "gtip_codes": ["8708", "8507", "8512"],
        "description": "Dünyanın en büyük otomotiv parçaları ve tedarikçiler fuarı"
    },
    {
        "id": 2, "name": "Hannover Messe",
        "location": "Hannover, Germany", "country": "Germany",
        "date": "2026-04-22", "end_date": "2026-04-26",
        "sector": ["Industrial Machinery", "Automation", "Electronics"],
        "website": "https://www.hannovermesse.de",
        "exhibitors_count": 6500, "visitors_count": 210000,
        "gtip_codes": ["8479", "8471", "8537"],
        "description": "Dünyanın en büyük endüstriyel teknoloji fuarı"
    },
    {
        "id": 3, "name": "Canton Fair (China Import Export Fair)",
        "location": "Guangzhou, China", "country": "China",
        "date": "2026-04-15", "end_date": "2026-05-05",
        "sector": ["Electronics", "Textiles", "Machinery", "Consumer Goods"],
        "website": "https://www.cantonfair.org.cn",
        "exhibitors_count": 25000, "visitors_count": 200000,
        "gtip_codes": ["8471", "6101", "8428"],
        "description": "Çin'in en büyük ithalat/ihracat fuarı, 3 aşamalı"
    },
    {
        "id": 4, "name": "Bauma Munich",
        "location": "Munich, Germany", "country": "Germany",
        "date": "2025-04-07", "end_date": "2025-04-13",
        "sector": ["Construction Equipment", "Mining", "Heavy Machinery"],
        "website": "https://bauma.de",
        "exhibitors_count": 3600, "visitors_count": 620000,
        "gtip_codes": ["8426", "8429", "8430"],
        "description": "Dünyanın en büyük inşaat makineleri fuarı"
    },
    {
        "id": 5, "name": "Interpack Düsseldorf",
        "location": "Düsseldorf, Germany", "country": "Germany",
        "date": "2026-05-07", "end_date": "2026-05-13",
        "sector": ["Packaging", "Food Processing", "Pharmaceutical"],
        "website": "https://www.interpack.com",
        "exhibitors_count": 2800, "visitors_count": 170000,
        "gtip_codes": ["8422", "8441", "8443"],
        "description": "Ambalaj ve işleme endüstrisinin en büyük fuarı"
    },
    {
        "id": 6, "name": "Medica Düsseldorf",
        "location": "Düsseldorf, Germany", "country": "Germany",
        "date": "2026-11-16", "end_date": "2026-11-19",
        "sector": ["Medical Devices", "Healthcare", "Pharmaceuticals"],
        "website": "https://www.medica.de",
        "exhibitors_count": 6200, "visitors_count": 120000,
        "gtip_codes": ["9018", "9019", "9021"],
        "description": "Dünyanın en büyük tıbbi cihaz fuarı"
    },
    {
        "id": 7, "name": "GITEX Technology Week",
        "location": "Dubai, UAE", "country": "UAE",
        "date": "2026-10-13", "end_date": "2026-10-17",
        "sector": ["Technology", "Software", "AI", "Cybersecurity"],
        "website": "https://www.gitex.com",
        "exhibitors_count": 5000, "visitors_count": 170000,
        "gtip_codes": ["8471", "8473", "8517"],
        "description": "Orta Doğu ve Afrika'nın en büyük teknoloji fuarı"
    },
    {
        "id": 8, "name": "Istanbul Furniture Fair (IVEX)",
        "location": "Istanbul, Turkey", "country": "Turkey",
        "date": "2026-01-22", "end_date": "2026-01-27",
        "sector": ["Furniture", "Home Decor", "Interior Design"],
        "website": "https://www.ivex.com.tr",
        "exhibitors_count": 1200, "visitors_count": 80000,
        "gtip_codes": ["9401", "9403", "9404"],
        "description": "Türkiye'nin en büyük mobilya fuarı"
    },
    {
        "id": 9, "name": "Big 5 Dubai (Construction)",
        "location": "Dubai, UAE", "country": "UAE",
        "date": "2026-11-23", "end_date": "2026-11-26",
        "sector": ["Construction", "Building Materials", "Real Estate"],
        "website": "https://www.thebig5.ae",
        "exhibitors_count": 3000, "visitors_count": 75000,
        "gtip_codes": ["7308", "6810", "8479"],
        "description": "Orta Doğu inşaat sektörünün en büyük fuarı"
    },
    {
        "id": 10, "name": "SIAL Paris (Food & Agriculture)",
        "location": "Paris, France", "country": "France",
        "date": "2026-10-19", "end_date": "2026-10-23",
        "sector": ["Food", "Agriculture", "Beverages"],
        "website": "https://www.sialparis.com",
        "exhibitors_count": 7400, "visitors_count": 310000,
        "gtip_codes": ["0207", "1905", "2009"],
        "description": "Dünyanın en büyük gıda fuarı"
    },
    {
        "id": 11, "name": "EMO Hannover (Machine Tools)",
        "location": "Hannover, Germany", "country": "Germany",
        "date": "2025-09-22", "end_date": "2025-09-27",
        "sector": ["Machine Tools", "Manufacturing", "CNC", "Robotics"],
        "website": "https://www.emo-hannover.de",
        "exhibitors_count": 2200, "visitors_count": 130000,
        "gtip_codes": ["8457", "8458", "8459"],
        "description": "Dünyanın en büyük takım tezgahları fuarı"
    },
    {
        "id": 12, "name": "Texworld Paris",
        "location": "Paris, France", "country": "France",
        "date": "2026-02-10", "end_date": "2026-02-13",
        "sector": ["Textiles", "Fashion", "Apparel"],
        "website": "https://texworld-paris.com",
        "exhibitors_count": 1500, "visitors_count": 25000,
        "gtip_codes": ["5208", "5512", "6101"],
        "description": "Küresel tekstil ve moda buluşması"
    },
    {
        "id": 13, "name": "Ambiente Frankfurt (Consumer Goods)",
        "location": "Frankfurt, Germany", "country": "Germany",
        "date": "2026-02-07", "end_date": "2026-02-11",
        "sector": ["Consumer Goods", "Gifts", "Home Textiles"],
        "website": "https://ambiente.messefrankfurt.com",
        "exhibitors_count": 4800, "visitors_count": 150000,
        "gtip_codes": ["6301", "6911", "7013"],
        "description": "Ev ve yaşam ürünleri için dünya lider fuarı"
    },
    {
        "id": 14, "name": "Wire & Tube Düsseldorf",
        "location": "Düsseldorf, Germany", "country": "Germany",
        "date": "2026-04-20", "end_date": "2026-04-24",
        "sector": ["Wire", "Cable", "Pipes", "Metal"],
        "website": "https://www.wire.de",
        "exhibitors_count": 2500, "visitors_count": 70000,
        "gtip_codes": ["7217", "7304", "7408"],
        "description": "Tel, kablo ve boru sektörünün lider fuarı"
    },
    {
        "id": 15, "name": "EuroCIS Düsseldorf (Retail Technology)",
        "location": "Düsseldorf, Germany", "country": "Germany",
        "date": "2026-02-18", "end_date": "2026-02-20",
        "sector": ["Retail", "POS", "Digital Signage", "Payments"],
        "website": "https://www.eurocis.com",
        "exhibitors_count": 500, "visitors_count": 17000,
        "gtip_codes": ["8471", "8537", "8528"],
        "description": "Perakende teknolojileri lider fuarı"
    },
]


class FairSearchRequest(BaseModel):
    keywords: Optional[List[str]] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    gtip_code: Optional[str] = None
    year: Optional[int] = None


class FairMatchRequest(BaseModel):
    product_keywords: List[str]
    gtip_codes: Optional[List[str]] = None
    target_countries: Optional[List[str]] = None


class ExhibitorAnalysisRequest(BaseModel):
    fair_name: str
    exhibitor_websites: List[str]
    your_products: List[str]
    gtip_code: Optional[str] = None


@router.get("/list")
async def list_fairs(
    sector: Optional[str] = None,
    country: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Tüm fuarları listele — filtrele"""
    fairs = GLOBAL_FAIRS.copy()

    if sector:
        fairs = [f for f in fairs if any(
            sector.lower() in s.lower() for s in f["sector"]
        )]

    if country:
        fairs = [f for f in fairs if country.lower() in f["country"].lower()]

    return {
        "total": len(fairs),
        "fairs": fairs
    }


@router.post("/match")
async def match_fairs(
    request: FairMatchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Ürün anahtar kelimelerini ve GTİP kodlarını en ilgili fuarlarla eşleştir.
    Groq AI ile skor hesaplanır.
    """
    matched = []

    for fair in GLOBAL_FAIRS:
        score = 0
        reasons = []

        # GTİP kodu eşleştirme (+40 puan)
        if request.gtip_codes:
            for gtip in request.gtip_codes:
                if any(gtip[:4] == fg[:4] for fg in fair.get("gtip_codes", [])):
                    score += 40
                    reasons.append(f"GTİP {gtip} eşleşmesi")
                    break

        # Keyword eşleştirme (+10 puan per keyword)
        fair_text = " ".join(fair["sector"]) + " " + fair["description"]
        for kw in request.product_keywords:
            if kw.lower() in fair_text.lower():
                score += 10
                reasons.append(f"'{kw}' sektörle eşleşiyor")

        # Ülke filtresi (+5 puan)
        if request.target_countries:
            if any(c.lower() in fair["country"].lower() for c in request.target_countries):
                score += 5
                reasons.append("Hedef ülkede")

        if score > 0:
            matched.append({
                **fair,
                "match_score": min(score, 100),
                "match_reasons": reasons,
                "relevance": "Yüksek" if score >= 40 else "Orta" if score >= 20 else "Düşük"
            })

    # Skora göre sırala
    matched.sort(key=lambda x: x["match_score"], reverse=True)

    # Groq ile açıklama ekle (varsa)
    groq_key = get_groq_key()
    summary = None
    if groq_key and matched:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            top3 = matched[:3]
            fair_names = ", ".join([f["name"] for f in top3])
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{
                    "role": "user",
                    "content": f"Dış ticaret danışmanı olarak, {', '.join(request.product_keywords)} satan bir Türk firması için {fair_names} fuarlarının neden önemli olduğunu 2 cümlede açıkla. Türkçe yaz."
                }],
                max_tokens=200
            )
            summary = response.choices[0].message.content
        except Exception as e:
            print(f"[Fairs Groq] {e}")

    return {
        "matched_fairs": matched[:20],
        "total_matched": len(matched),
        "ai_summary": summary,
        "keywords_used": request.product_keywords,
        "gtip_codes_used": request.gtip_codes or []
    }


@router.post("/analyze-exhibitors")
async def analyze_exhibitors(
    request: ExhibitorAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Fuar katılımcı web sitelerini tara ve sizinle eşleşenleri bul.
    ContactFinder + Groq AI ile analiz.
    """
    if not request.exhibitor_websites:
        raise HTTPException(status_code=400, detail="En az bir katılımcı web sitesi girin")

    # Web sitelerinden iletişim bilgisi çek
    contact_results = await ContactFinderService.find_contacts_bulk(
        request.exhibitor_websites[:20]
    )

    # Groq ile eşleştirme analizi
    groq_key = get_groq_key()
    analyzed = []

    for i, website in enumerate(request.exhibitor_websites[:20]):
        contacts = contact_results[i] if i < len(contact_results) else {}

        result = {
            "website": website,
            "emails": contacts.get("emails", []),
            "phones": contacts.get("phones", []),
            "social_media": contacts.get("social_media", {}),
            "match_score": 0,
            "is_potential_customer": False,
            "ai_analysis": None
        }

        # AI ile eşleştirme (0.5 saniye gecikme ile rate limit'i aşmamak için)
        if groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=groq_key)
                await asyncio.sleep(0.5)
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{
                        "role": "user",
                        "content": f"Web sitesi: {website}\nBizim ürünlerimiz: {', '.join(request.your_products)}\nGTİP: {request.gtip_code or 'Belirtilmedi'}\n\nBu firma bizim potansiyel müşterimiz mi? Kısa bir değerlendirme yap (max 2 cümle, Türkçe). Eşleşme skoru 0-100 ver."
                    }],
                    max_tokens=150
                )
                ai_text = response.choices[0].message.content
                result["ai_analysis"] = ai_text
                # Basit skor çıkar
                import re
                score_match = re.search(r'\b(\d{1,3})\b', ai_text)
                if score_match:
                    score = int(score_match.group(1))
                    if 0 <= score <= 100:
                        result["match_score"] = score
                        result["is_potential_customer"] = score >= 50
            except Exception:
                result["match_score"] = 50  # Varsayılan

        analyzed.append(result)

    # Skora göre sırala
    analyzed.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "fair_name": request.fair_name,
        "total_analyzed": len(analyzed),
        "potential_customers": [a for a in analyzed if a["is_potential_customer"]],
        "all_results": analyzed,
        "tip": "E-posta adresleri bulunan firmalara Auto Mail ile kampanya gönderebilirsiniz"
    }


@router.get("/upcoming")
async def get_upcoming_fairs(
    current_user: User = Depends(get_current_active_user)
):
    """Yaklaşan fuarların listesi"""
    from datetime import date
    today = date.today().isoformat()
    upcoming = [f for f in GLOBAL_FAIRS if f["date"] >= today]
    upcoming.sort(key=lambda x: x["date"])
    return {"upcoming_fairs": upcoming[:10], "total": len(upcoming)}


@router.get("/sectors")
async def get_fair_sectors(
    current_user: User = Depends(get_current_active_user)
):
    """Fuar sektörlerini listele"""
    sectors = set()
    for fair in GLOBAL_FAIRS:
        sectors.update(fair["sector"])
    return {"sectors": sorted(list(sectors))}
