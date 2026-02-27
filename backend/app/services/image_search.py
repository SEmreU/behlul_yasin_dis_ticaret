"""
Görsel Arama Servisi
Groq Vision (llama-3.2-11b-vision-preview) ile ürün analizi
"""
import base64
import json
import os
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from PIL import Image


def _get_groq_key() -> str:
    """DB'den veya env'den Groq API key al"""
    try:
        from app.core.database import SessionLocal
        from app.models.api_setting import ApiSetting
        db = SessionLocal()
        s = db.query(ApiSetting).filter(ApiSetting.key_name == "GROQ_API_KEY").first()
        db.close()
        if s and s.key_value:
            return base64.b64decode(s.key_value.encode()).decode()
    except Exception:
        pass
    try:
        from app.core.config import settings
        return getattr(settings, "GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
    except Exception:
        return os.getenv("GROQ_API_KEY", "")


class ImageSearchService:
    """Görsel arama servisi — Groq Vision ile"""

    @staticmethod
    async def search_by_image(
        image_path: str,
        db: Session,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Görsel ile ürün ara.
        1. Görseli Groq Vision ile analiz et (kategori, keywords, açıklama)
        2. DB'de benzer ürünleri ara
        """
        # Görseli kontrol et
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception:
            raise ValueError("Görsel yüklenemedi veya geçersiz format")

        # Groq Vision ile analiz
        product_info = await ImageSearchService._analyze_with_groq_vision(image_path)

        # DB'de ara
        products = ImageSearchService._search_in_database(
            db,
            category=product_info.get("category"),
            keywords=product_info.get("keywords", []),
            max_results=max_results,
        )

        return products

    @staticmethod
    async def _analyze_with_groq_vision(image_path: str) -> Dict:
        """
        Groq llama-3.2-11b-vision-preview ile görsel analizi.
        Ücretsiz, hızlı, OpenAI'a gerek yok.
        """
        groq_key = _get_groq_key()

        if not groq_key:
            return {
                "category": "unknown",
                "subcategory": "unknown",
                "keywords": [],
                "description": "GROQ_API_KEY eksik. Ayarlar'a ekleyin.",
            }

        # Görseli base64'e çevir
        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return {"category": "unknown", "keywords": [], "description": str(e)}

        prompt = """Bu ürün görselini analiz et. Aşağıdaki JSON formatında yanıt ver (başka hiçbir şey yazma):
{
  "category": "ürün kategorisi (ör: elektronik, tekstil, makine, mobilya, gıda)",
  "subcategory": "alt kategori (ör: akıllı telefon, t-shirt, CNC makinesi)",
  "keywords": ["kelime1", "kelime2", "kelime3", "kelime4"],
  "description": "ürünün kısa Türkçe açıklaması"
}"""

        try:
            from groq import Groq
            client = Groq(api_key=groq_key)

            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
                temperature=0.2,
            )

            raw = response.choices[0].message.content.strip()

            # JSON bloğunu temizle (```json ... ``` sarmalı olabilir)
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            return json.loads(raw)

        except json.JSONDecodeError:
            # JSON parse edilemedi ama yanıt var — keyword olarak kullan
            return {
                "category": "unknown",
                "subcategory": "unknown",
                "keywords": [],
                "description": raw if "raw" in dir() else "Parse hatası",
            }
        except Exception as e:
            print(f"[Groq Vision] Error: {e}")
            return {
                "category": "unknown",
                "subcategory": "unknown",
                "keywords": [],
                "description": str(e),
            }

    @staticmethod
    def _search_in_database(
        db: Session,
        category: Optional[str] = None,
        keywords: List[str] = None,
        max_results: int = 10,
    ) -> List[Dict]:
        """DB'de ürün ara"""
        try:
            from app.models.product import Product
            query = db.query(Product)

            if category and category not in ("unknown", ""):
                query = query.filter(Product.category == category)

            if keywords:
                for keyword in keywords[:3]:  # En fazla 3 keyword filtrele
                    query = query.filter(
                        Product.descriptions.contains(keyword.lower())
                    )

            products = query.limit(max_results).all()

            return [
                {
                    "id": p.id,
                    "gtip_code": p.gtip_code,
                    "oem_code": p.oem_code,
                    "category": p.category,
                    "subcategory": p.subcategory,
                    "descriptions": p.descriptions,
                    "image_url": p.image_url,
                    "match_score": 85,
                }
                for p in products
            ]
        except Exception as e:
            print(f"[ImageSearch] DB error: {e}")
            return []
