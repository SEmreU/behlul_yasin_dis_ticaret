from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import httpx
from app.models.product import Product
from app.models.company import Company


class ProductSearchService:
    """Akıllı ürün arama servisi - 8 dilde arama"""

    SUPPORTED_LANGUAGES = ['tr', 'en', 'es', 'ru', 'ar', 'fr', 'de', 'zh']

    @staticmethod
    async def search_products(
        db: Session,
        query: str,
        language: str = 'tr',
        search_type: str = 'text',
        max_results: int = 50
    ) -> List[Dict]:
        """
        Ana arama metodu — search_type'a göre doğru servisi çağırır.
        Sonuçları frontend'in beklediği ortak formata dönüştürür.
        """
        try:
            if search_type == 'gtip':
                products = ProductSearchService.search_by_gtip(db, query)
                return [
                    {
                        "id": p.id,
                        "title": getattr(p, 'category', '') or 'Ürün',
                        "gtip_code": getattr(p, 'gtip_code', ''),
                        "oem_code": getattr(p, 'oem_code', ''),
                        "country": "",
                        "source": "DB/GTİP",
                        "url": None,
                    }
                    for p in products[:max_results]
                ]
            elif search_type == 'oem':
                products = ProductSearchService.search_by_oem(db, query)
                return [
                    {
                        "id": p.id,
                        "title": getattr(p, 'category', '') or 'Ürün',
                        "gtip_code": getattr(p, 'gtip_code', ''),
                        "oem_code": getattr(p, 'oem_code', ''),
                        "country": "",
                        "source": "DB/OEM",
                        "url": None,
                    }
                    for p in products[:max_results]
                ]
            else:
                # text search — çoklu dil
                langs = [language] if language != 'tr' else ['tr', 'en']
                results = await ProductSearchService.search_by_name_multilang(db, query, langs)
                return results[:max_results]
        except Exception as e:
            # Veritabanında tablo yoksa boş liste döndür (Supabase'de henüz veri girilmemiş olabilir)
            print(f"[Search] {e}")
            return []


    @staticmethod
    async def translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """
        Google Translate API ile çeviri
        Production'da: Google Cloud Translation API kullanın

        Args:
            text: Çevrilecek metin
            target_lang: Hedef dil
            source_lang: Kaynak dil (default: auto-detect)

        Returns:
            Çevrilmiş metin
        """
        # TODO: Google Cloud Translation API entegrasyonu
        # Şimdilik basit placeholder
        return text

    @staticmethod
    def search_by_gtip(db: Session, gtip_code: str) -> List[Product]:
        """
        GTIP/HS koduna göre ürün ara

        Args:
            gtip_code: GTIP/HS code (örn: "8409.91")

        Returns:
            Liste of Product
        """
        return db.query(Product).filter(
            Product.gtip_code.like(f"{gtip_code}%")
        ).limit(100).all()

    @staticmethod
    def search_by_oem(db: Session, oem_code: str) -> List[Product]:
        """
        OEM/Part koduna göre ürün ara

        Args:
            oem_code: OEM/Part number

        Returns:
            Liste of Product
        """
        return db.query(Product).filter(
            Product.oem_code.ilike(f"%{oem_code}%")
        ).limit(100).all()

    @staticmethod
    async def search_by_name_multilang(
        db: Session,
        query: str,
        languages: List[str] = None
    ) -> List[Dict]:
        """
        Çoklu dilde ürün ismi araması

        Args:
            query: Arama terimi
            languages: Aranacak diller (default: tümü)

        Returns:
            Ürün sonuçları (deduplicated)
        """
        if languages is None:
            languages = ProductSearchService.SUPPORTED_LANGUAGES

        results = []
        seen_ids = set()

        # Her dilde ara
        for lang in languages:
            # Translations dict'te arama yap (PostgreSQL JSON query)
            products = db.query(Product).filter(
                Product.descriptions[lang].astext.ilike(f"%{query}%")
            ).limit(50).all()

            for product in products:
                if product.id not in seen_ids:
                    results.append({
                        "id": product.id,
                        "gtip_code": product.gtip_code,
                        "oem_code": product.oem_code,
                        "name": product.descriptions.get(lang, ""),
                        "language": lang,
                        "category": product.category,
                    })
                    seen_ids.add(product.id)

        return results

    @staticmethod
    async def verify_term_with_dictionary(term: str, source_lang: str, target_lang: str) -> Dict:
        """
        IATE veya Cambridge Dictionary ile terim doğrulama

        Args:
            term: Doğrulanacak terim
            source_lang: Kaynak dil
            target_lang: Hedef dil

        Returns:
            Dictionary verification result
        """
        # TODO: IATE (Inter-Active Terminology for Europe) API entegrasyonu
        # https://iate.europa.eu/

        # Placeholder response
        return {
            "verified": True,
            "term": term,
            "translations": {
                target_lang: term  # Gerçek API'den gelecek
            },
            "confidence": 0.8
        }

    @staticmethod
    async def image_search(image_url: str) -> List[Dict]:
        """
        Görüntü işleme ile ürün arama (Reverse image search)

        Args:
            image_url: Ürün resmi URL

        Returns:
            Benzer ürünler
        """
        # TODO: Google Vision API veya Yandex Image Search
        # 1. Image upload
        # 2. Feature extraction (OpenCV/PIL)
        # 3. Reverse image search
        # 4. Scrape sonuçlar

        # Placeholder
        return []

    @staticmethod
    async def search_with_valentin_simulation(
        query: str,
        target_country: str,
        language: str
    ) -> List[Dict]:
        """
        Valentin.app simülasyonu - Hedef ülke IP'sinden arama

        Args:
            query: Arama sorgusu
            target_country: Hedef ülke (DE, US, CN...)
            language: Arama dili

        Returns:
            B2B platform sonuçları (Alibaba, Tradeatlas vb.)
        """
        # TODO: Playwright ile proxy kullanımı
        # 1. Hedef ülke proxy al (Residential proxy)
        # 2. Playwright browser açarakçıkarma
        # 3. Alibaba/Tradeatlas'ta ara
        # 4. Sonuçları scrape et

        # Placeholder
        return []
