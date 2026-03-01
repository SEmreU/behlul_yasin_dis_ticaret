from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.product_search import ProductSearchService, CustomerSearchService, SearchParams
from app.services.image_search import ImageSearchService
from app.services.activity_logger import log_activity_safe, Module
import os
import uuid

router = APIRouter()


class ProductSearchRequest(BaseModel):
    """Ürün arama isteği"""
    query: str
    language: str = "tr"
    search_type: str = "text"  # text, gtip, oem
    max_results: int = 50
    country: str = ""  # Hedef ülke filtresi


class CustomerSearchRequest(BaseModel):
    """Potansiyel müşteri arama isteği — tüm form alanları"""
    product_name: str
    gtip_code: str = ""
    oem_no: str = ""
    target_country: str = ""
    search_language: str = "en"
    related_sectors: str = ""
    competitor_brands: str = ""
    search_engines: List[str] = []   # ["Google", "Bing", ...]
    db_sources: List[str] = []       # ["TradeAtlas", "Panjiva", ...]
    max_results: int = 50


class TranslateRequest(BaseModel):
    """Çeviri isteği"""
    text: str
    source_lang: str
    target_lang: str


@router.post("/customers")
async def search_customers(
    request: CustomerSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Potansiyel müşteri arama — seçili arama motorları + ticaret DB'lerini paralel çalıştırır.

    Dönen yapı:
    {
      "results": [...],          // relevance_score sıralaması
      "by_source": {...},        // kaynak bazında
      "total": int,
      "sources_searched": [...]
    }
    """
    if not request.product_name.strip():
        raise HTTPException(status_code=400, detail="Ürün adı boş olamaz")

    try:
        params = SearchParams(
            product_name=request.product_name,
            gtip_code=request.gtip_code,
            oem_no=request.oem_no,
            target_country=request.target_country,
            search_language=request.search_language,
            related_sectors=request.related_sectors,
            competitor_brands=request.competitor_brands,
        )

        # Kaynak seçimi boşsa varsayılan : tüm kaynaklar
        engines = request.search_engines or ["Google", "Bing", "DuckDuckGo"]
        dbs = request.db_sources or ["Europages", "TradeKey"]

        per_source = max(5, request.max_results // max(len(engines) + len(dbs), 1) + 2)

        data = await CustomerSearchService.search_all_sources(
            params=params,
            search_engines=engines,
            db_sources=dbs,
            max_per_source=per_source,
        )

        # Aktivite logla
        log_activity_safe(
            db, current_user.id,
            module=Module.SEARCH,
            action=f"Müşteri arama: {request.product_name[:60]}",
            credits_used=len(engines) + len(dbs),
            status="success",
            meta_data={
                "product": request.product_name,
                "country": request.target_country,
                "engines": engines,
                "dbs": dbs,
                "total": data["total"],
            },
        )

        return {
            "results": data["results"][:request.max_results],
            "by_source": data["by_source"],
            "total": data["total"],
            "sources_searched": engines + dbs,
        }
    except Exception as e:
        import logging
        logging.getLogger("search").warning("Customer search error: %s", str(e)[:200])
        return {
            "results": [],
            "by_source": {},
            "total": 0,
            "sources_searched": [],
            "error": "Arama sırasında hata oluştu, lütfen tekrar deneyin."
        }


@router.post("/product")
async def search_product(
    request: ProductSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ürün ara (8 dil desteği) — geriye dönük uyumluluk endpoint'i
    """
    try:
        results = await ProductSearchService.search_products(
            db=db,
            query=request.query,
            language=request.language,
            search_type=request.search_type,
            max_results=request.max_results,
            country=request.country,
        )

        # Aktivite logla
        log_activity_safe(
            db, current_user.id,
            module=Module.SEARCH,
            action=f"Ürün arama: {request.query[:80]}",
            credits_used=1,
            status="success",
            meta_data={
                "query": request.query,
                "language": request.language,
                "search_type": request.search_type,
                "country": request.country,
                "results_count": len(results)
            }
        )

        return {
            "query": request.query,
            "language": request.language,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        import logging
        logging.getLogger("search").warning("Product search error: %s", str(e)[:200])
        return {
            "query": request.query,
            "language": request.language,
            "results_count": 0,
            "results": [],
            "error": "Arama sırasında hata oluştu, lütfen tekrar deneyin."
        }


@router.post("/image-search")
async def image_search(
    file: UploadFile = File(...),
    max_results: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Görsel ile ürün ara
    
    **Özellikler:**
    - GPT-4 Vision ile görsel analizi
    - Otomatik kategori tespiti
    - Benzer ürün eşleştirme
    
    **Gerekli:**
    - OpenAI API key (GPT-4 Vision)
    """
    # Dosyayı geçici olarak kaydet
    temp_dir = "/tmp/image_search"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_extension = file.filename.split('.')[-1]
    temp_filename = f"{uuid.uuid4()}.{file_extension}"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        # Dosyayı kaydet
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Görsel araması yap
        results = await ImageSearchService.search_by_image(
            image_path=temp_path,
            db=db,
            max_results=max_results
        )
        
        return {
            "filename": file.filename,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Geçici dosyayı sil
        if os.path.exists(temp_path):
            os.remove(temp_path)

    results = []

    # Arama tipine göre işlem
    if request.search_type == "gtip":
        products = ProductSearchService.search_by_gtip(db, request.query)
        results = [
            {
                "id": p.id,
                "gtip_code": p.gtip_code,
                "oem_code": p.oem_code,
                "category": p.category,
                "descriptions": p.descriptions,
            }
            for p in products
        ]

    elif request.search_type == "oem":
        products = ProductSearchService.search_by_oem(db, request.query)
        results = [
            {
                "id": p.id,
                "gtip_code": p.gtip_code,
                "oem_code": p.oem_code,
                "descriptions": p.descriptions,
            }
            for p in products
        ]

    elif request.search_type == "multilang":
        results = await ProductSearchService.search_by_name_multilang(
            db, request.query, request.languages
        )

    elif request.search_type == "name":
        # Tek dilde arama (legacy)
        results = await ProductSearchService.search_by_name_multilang(
            db, request.query, ["tr", "en"]
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid search_type: {request.search_type}"
        )

    # Kontör düş
    current_user.query_credits -= 1
    db.commit()

    return {
        "results": results,
        "total": len(results),
        "search_type": request.search_type
    }


@router.post("/translate")
async def translate_term(
    text: str,
    target_lang: str,
    source_lang: str = "auto",
    current_user: User = Depends(get_current_active_user)
):
    """
    Terim çevirisi (Google Translate)

    Args:
        text: Çevrilecek metin
        target_lang: Hedef dil (tr, en, de...)
        source_lang: Kaynak dil (default: auto)

    Returns:
        Çevrilmiş metin
    """
    translated = await ProductSearchService.translate_text(
        text, target_lang, source_lang
    )

    return {
        "original": text,
        "translated": translated,
        "source_lang": source_lang,
        "target_lang": target_lang
    }


@router.post("/verify-term")
async def verify_dictionary_term(
    term: str,
    source_lang: str,
    target_lang: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    IATE/Cambridge Dictionary ile terim doğrulama

    Teknik terimlerin doğru çevrildiğini kontrol eder

    Args:
        term: Doğrulanacak terim
        source_lang: Kaynak dil
        target_lang: Hedef dil
    """
    verification = await ProductSearchService.verify_term_with_dictionary(
        term, source_lang, target_lang
    )

    return verification


@router.post("/image-search")
async def image_based_search(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Görüntü işleme ile ürün arama

    Ürün resmini yükleyin, benzer ürünleri bulun

    **Süreç:**
    1. Image upload
    2. OpenCV/Google Vision ile feature extraction
    3. Reverse image search (Yandex, Google)
    4. Sonuçları scrape et

    **Kontör:** 2 credit harcar (ağır işlem)
    """
    if current_user.query_credits < 2:
        raise HTTPException(
            status_code=403,
            detail="Insufficient credits. Image search requires 2 credits."
        )

    # TODO: Image processing
    # 1. Save uploaded image
    # 2. Extract features (OpenCV/PIL)
    # 3. Reverse image search
    # 4. Return results

    # Kontör düş
    current_user.query_credits -= 2
    db.commit()

    return {
        "message": "Image search feature coming soon",
        "filename": image.filename,
        "status": "processing"
    }
