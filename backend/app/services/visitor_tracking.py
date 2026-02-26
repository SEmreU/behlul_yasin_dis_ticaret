from sqlalchemy.orm import Session
from typing import Optional, Dict
import httpx
from app.models.visitor import VisitorIdentification
from app.models.company import Company
import hashlib


class VisitorTrackingService:
    """Ziyaretçi kimliklendirme servisi"""

    @staticmethod
    async def get_ip_geolocation(ip_address: str) -> Dict:
        """
        IP adresinden lokasyon bilgisi al

        Uses ipapi.co (ücretsiz tier: 1000 req/day)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://ipapi.co/{ip_address}/json/",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "latitude": data.get("latitude"),
                        "longitude": data.get("longitude"),
                        "city": data.get("city"),
                        "country": data.get("country_name"),
                        "org": data.get("org"),  # ISP/Organization
                    }
        except Exception as e:
            print(f"IP geolocation error: {e}")

        return {}

    @staticmethod
    def generate_fingerprint(user_agent: str, ip_address: str) -> str:
        """Browser fingerprint oluştur"""
        data = f"{user_agent}{ip_address}".encode()
        return hashlib.sha256(data).hexdigest()[:32]

    @staticmethod
    async def identify_company_by_gps(
        db: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 0.5
    ) -> Optional[Company]:
        """
        GPS koordinatlarına yakın firma bul

        Args:
            latitude: Enlem
            longitude: Boylam
            radius_km: Arama yarıçapı (km)

        Returns:
            Company or None
        """
        # Haversine formula ile yakın firmaları bul
        # Simplified: Gerçek production'da PostGIS kullanılmalı
        companies = db.query(Company).filter(
            Company.latitude.isnot(None),
            Company.longitude.isnot(None)
        ).all()

        for company in companies:
            distance = VisitorTrackingService._calculate_distance(
                latitude, longitude,
                company.latitude, company.longitude
            )
            if distance <= radius_km:
                return company

        return None

    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        İki GPS koordinatı arasındaki mesafeyi hesapla (Haversine)

        Returns: Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth radius in km

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    @staticmethod
    async def track_visitor(
        db: Session,
        session_id: str,
        ip_address: str,
        user_agent: str,
        referer: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_permission_granted: bool = False
    ) -> VisitorIdentification:
        """
        Ziyaretçiyi tracking sisteme kaydet ve firma eşleştirmeyi dene

        Args:
            session_id: Unique session identifier
            ip_address: Client IP
            user_agent: Browser user agent
            referer: HTTP Referer header
            latitude: GPS latitude (if permission granted)
            longitude: GPS longitude (if permission granted)
            location_permission_granted: GPS izni verildi mi?

        Returns:
            VisitorIdentification instance
        """
        # Browser fingerprint oluştur
        fingerprint = VisitorTrackingService.generate_fingerprint(user_agent, ip_address)

        identified_company = None
        confidence_score = 0.0
        location_source = None
        country = None
        city = None

        # 1. GPS ile firma eşleştir (öncelikli)
        if location_permission_granted and latitude and longitude:
            identified_company = await VisitorTrackingService.identify_company_by_gps(
                db, latitude, longitude, radius_km=0.5
            )
            if identified_company:
                confidence_score = 0.9  # Yüksek güven skoru
                location_source = "gps"

        # 2. GPS yoksa IP geolocation kullan
        if not identified_company:
            geo_data = await VisitorTrackingService.get_ip_geolocation(ip_address)
            if geo_data:
                latitude = geo_data.get("latitude")
                longitude = geo_data.get("longitude")
                city = geo_data.get("city")
                country = geo_data.get("country")
                location_source = "ip_geolocation"

                # IP bazlı lokasyonla firma eşleştir (daha geniş yarıçap)
                if latitude and longitude:
                    identified_company = await VisitorTrackingService.identify_company_by_gps(
                        db, latitude, longitude, radius_km=5.0  # 5km yarıçap
                    )
                    if identified_company:
                        confidence_score = 0.5  # Orta güven skoru

        # Visitor identification oluştur
        visitor = VisitorIdentification(
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            latitude=latitude,
            longitude=longitude,
            location_source=location_source,
            identified_company_id=identified_company.id if identified_company else None,
            confidence_score=confidence_score,
            country=country,
            city=city,
            browser_fingerprint=fingerprint,
            location_permission_granted=location_permission_granted,
        )

        db.add(visitor)
        db.commit()
        db.refresh(visitor)

        return visitor
