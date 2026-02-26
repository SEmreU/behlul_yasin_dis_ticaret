"""
Görsel Arama Servisi
OpenCV + GPT-4 Vision ile ürün arama
"""
from PIL import Image
import numpy as np
import base64
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.product import Product


class ImageSearchService:
    """Görsel arama servisi"""
    
    @staticmethod
    async def search_by_image(
        image_path: str,
        db: Session,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Görsel ile ürün ara
        
        Args:
            image_path: Görsel dosya yolu
            db: Database session
            max_results: Maksimum sonuç sayısı
            
        Returns:
            Bulunan ürünler listesi
        """
        # 1. Görseli kontrol et
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception:
            raise ValueError("Görsel yüklenemedi veya geçersiz format")
        
        # 2. GPT-4 Vision ile analiz et
        product_info = await ImageSearchService._analyze_with_gpt4_vision(image_path)
        
        # 3. Database'de benzer ürünleri ara
        products = ImageSearchService._search_in_database(
            db,
            category=product_info.get('category'),
            keywords=product_info.get('keywords', []),
            max_results=max_results
        )
        
        return products
    
    @staticmethod
    async def _analyze_with_gpt4_vision(image_path: str) -> Dict:
        """
        GPT-4 Vision ile görsel analizi
        
        Args:
            image_path: Görsel dosya yolu
            
        Returns:
            {
                'category': 'elektronik',
                'subcategory': 'telefon',
                'keywords': ['samsung', 'galaxy', 'smartphone'],
                'description': 'Samsung Galaxy akıllı telefon'
            }
        """
        # API key kontrolü
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-placeholder":
            print("[Warning] OpenAI API key yok, mock data dönüyor")
            return {
                'category': 'unknown',
                'subcategory': 'unknown',
                'keywords': [],
                'description': 'API key gerekli'
            }
        
        try:
            from openai import OpenAI
            
            # Görseli base64'e çevir
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Bu ürünü analiz et ve şu bilgileri ver:
1. Kategori (elektronik, tekstil, makine, vb.)
2. Alt kategori
3. Anahtar kelimeler (en az 3)
4. Kısa açıklama

JSON formatında döndür:
{
  "category": "...",
  "subcategory": "...",
  "keywords": ["...", "...", "..."],
  "description": "..."
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # JSON parse et
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"GPT-4 Vision error: {e}")
            return {
                'category': 'unknown',
                'subcategory': 'unknown',
                'keywords': [],
                'description': str(e)
            }
    
    @staticmethod
    def _search_in_database(
        db: Session,
        category: Optional[str] = None,
        keywords: List[str] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Database'de ürün ara
        
        Args:
            db: Database session
            category: Kategori filtresi
            keywords: Anahtar kelimeler
            max_results: Maksimum sonuç
            
        Returns:
            Bulunan ürünler
        """
        query = db.query(Product)
        
        # Kategori filtresi
        if category and category != 'unknown':
            query = query.filter(Product.category == category)
        
        # Anahtar kelime araması
        if keywords:
            # JSON içinde arama (PostgreSQL)
            for keyword in keywords:
                query = query.filter(
                    Product.descriptions.contains(keyword.lower())
                )
        
        products = query.limit(max_results).all()
        
        return [
            {
                'id': p.id,
                'gtip_code': p.gtip_code,
                'oem_code': p.oem_code,
                'category': p.category,
                'subcategory': p.subcategory,
                'descriptions': p.descriptions,
                'image_url': p.image_url,
                'match_score': 85  # Basit scoring
            }
            for p in products
        ]
    
    @staticmethod
    def extract_features_opencv(image_path: str) -> np.ndarray:
        """
        Görsel özelliklerini çıkar (Stub - OpenCV bağımlılığı kaldırıldı)
        """
        print("[Warning] extract_features_opencv devredışı (cloud compatibility)")
        return np.array([])
