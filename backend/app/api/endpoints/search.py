from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.product_search import ProductSearchService
from app.services.image_search import ImageSearchService
import os
import uuid

router = APIRouter()


class ProductSearchRequest(BaseModel):
    """Ürün arama isteği"""
    query: str
    language: str = "tr"
    search_type: str = "text"  # text, gtip, oem
    max_results: int = 50


class TranslateRequest(BaseModel):
    """Çeviri isteği"""
    text: str
    source_lang: str
    target_lang: str


@router.post("/product")
async def search_product(
    request: ProductSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ürün ara (8 dil desteği)
    
    **Desteklenen Diller:**
    - tr (Türkçe)
    - en (English)
    - de (Deutsch)
    - ru (Русский)
    - ar (العربية)
    - fr (Français)
    - es (Español)
    - zh (中文)
    
    **Arama Tipleri:**
    - text: Metin araması
    - gtip: GTIP kodu ile
    - oem: OEM kodu ile
    """
    results = await ProductSearchService.search_products(
        db=db,
        query=request.query,
        language=request.language,
        search_type=request.search_type,
        max_results=request.max_results
    )
    
    return {
        "query": request.query,
        "language": request.language,
        "results_count": len(results),
        "results": results
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
