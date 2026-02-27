"""
Marketplace Scrapers — ScraperAPI tabanlı
Platformlar: TradeKey, ECPlaza, eWorldTrade, IndiaMart, EC21, Kompass, Thomasnet
marketplace_scrapers.py artık b2b_scraper.py'den import eder, kod tekrarı olmaz.
"""

from typing import List, Dict
from app.services.b2b_scraper import (
    B2BScraperService,
    TradeKeyScraper,
    ECPlazaScraper,
    IndiaMARTScraper,
    EC21Scraper,
    KompassScraper,
    ThomasnetScraper,
    get_api_key,
)


class MarketplaceScraperService:
    """
    B2B marketplace aramaları için ana servis.
    Tüm scraper'lar b2b_scraper.py'den gelir.
    """

    @staticmethod
    async def search_all_marketplaces(
        search_query: str,
        platforms: List[str] = None,
        search_type: str = "products",
    ) -> Dict[str, List[Dict]]:
        """
        Birden fazla platformda eş zamanlı ara.

        Args:
            search_query: Ürün adı veya OEM numarası
            platforms: Platform listesi (None ise varsayılan)
            search_type: 'products' veya 'rfqs'

        Returns:
            {platform_name: [result_dict, ...]}
        """
        if platforms is None:
            platforms = ["tradekey", "indiamart", "ec21", "kompass", "thomasnet"]

        if search_type == "rfqs":
            # RFQ odaklı arama
            rfq_platforms = {p for p in platforms if p in ("tradekey",)}
            product_platforms = [p for p in platforms if p not in rfq_platforms]

            results = {}

            # RFQ araması
            if "tradekey" in rfq_platforms:
                results["tradekey"] = await TradeKeyScraper.search_rfqs(search_query)

            # Ürün araması
            if product_platforms:
                product_results = await B2BScraperService.search_all_platforms(
                    search_query, platforms=product_platforms
                )
                results.update(product_results)

            return results

        # Standart ürün araması
        return await B2BScraperService.search_all_platforms(
            search_query, platforms=platforms
        )

    @staticmethod
    def get_supported_platforms() -> List[Dict]:
        """Desteklenen platformları listele"""
        api_key = get_api_key()
        has_key = bool(api_key)

        return [
            # Çin
            {"id": "alibaba",        "name": "Alibaba.com",         "country": "China",       "live": has_key, "type": "product"},
            {"id": "made-in-china",  "name": "Made-in-China",       "country": "China",       "live": has_key, "type": "product"},
            {"id": "dhgate",         "name": "DHgate",              "country": "China",       "live": has_key, "type": "product"},
            {"id": "aliexpress",     "name": "AliExpress",          "country": "China",       "live": has_key, "type": "product"},
            {"id": "1688",           "name": "1688.com (Fabrika)",  "country": "China",       "live": has_key, "type": "product"},
            {"id": "global-sources", "name": "Global Sources",      "country": "China",       "live": has_key, "type": "product"},
            {"id": "yiwugo",         "name": "Yiwugo (Yiwu)",       "country": "China",       "live": has_key, "type": "product"},
            # Küresel B2B
            {"id": "tradekey",       "name": "TradeKey",            "country": "Global",      "live": has_key, "type": "rfq"},
            {"id": "ec21",           "name": "EC21",                "country": "Korea/Global","live": has_key, "type": "product"},
            {"id": "indiamart",      "name": "IndiaMart",           "country": "India",       "live": has_key, "type": "product"},
            {"id": "tradeindia",     "name": "TradeIndia",          "country": "India",       "live": has_key, "type": "product"},
            {"id": "ecplaza",        "name": "ECPlaza",             "country": "Korea",       "live": has_key, "type": "product"},
            {"id": "kompass",        "name": "Kompass",             "country": "Europe",      "live": has_key, "type": "company"},
            # ABD
            {"id": "thomasnet",      "name": "Thomasnet",           "country": "USA",         "live": has_key, "type": "company"},
        ]
