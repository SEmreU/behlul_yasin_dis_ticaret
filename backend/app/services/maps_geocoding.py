"""
Google Maps Geocoding Servisi
"""
from typing import Optional, Dict
from app.core.config import settings


class MapsGeocodingService:
    """Google Maps geocoding servisi"""
    
    @staticmethod
    def geocode_address(address: str) -> Optional[Dict]:
        """
        Adres → Koordinat
        
        Args:
            address: Adres metni
            
        Returns:
            {
                'lat': 41.0082,
                'lng': 28.9784,
                'formatted_address': 'Istanbul, Turkey'
            }
        """
        # API key kontrolü
        if not settings.GOOGLE_MAPS_API_KEY or settings.GOOGLE_MAPS_API_KEY == "placeholder":
            print("[Warning] Google Maps API key yok, mock data dönüyor")
            return {
                'lat': 0.0,
                'lng': 0.0,
                'formatted_address': address
            }
        
        try:
            import googlemaps
            
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            result = gmaps.geocode(address)
            
            if result:
                location = result[0]['geometry']['location']
                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': result[0]['formatted_address'],
                    'place_id': result[0].get('place_id'),
                    'types': result[0].get('types', [])
                }
            
            return None
            
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
    
    @staticmethod
    def reverse_geocode(lat: float, lng: float) -> Optional[Dict]:
        """
        Koordinat → Adres
        
        Args:
            lat: Enlem
            lng: Boylam
            
        Returns:
            Adres bilgisi
        """
        if not settings.GOOGLE_MAPS_API_KEY or settings.GOOGLE_MAPS_API_KEY == "placeholder":
            return {'formatted_address': f"Lat: {lat}, Lng: {lng}"}
        
        try:
            import googlemaps
            
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            result = gmaps.reverse_geocode((lat, lng))
            
            if result:
                return {
                    'formatted_address': result[0]['formatted_address'],
                    'place_id': result[0].get('place_id'),
                    'types': result[0].get('types', [])
                }
            
            return None
            
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return None
    
    @staticmethod
    def get_place_details(place_id: str) -> Optional[Dict]:
        """
        Place ID'den detaylı bilgi al
        
        Args:
            place_id: Google Maps Place ID
            
        Returns:
            Detaylı yer bilgisi
        """
        if not settings.GOOGLE_MAPS_API_KEY or settings.GOOGLE_MAPS_API_KEY == "placeholder":
            return None
        
        try:
            import googlemaps
            
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            result = gmaps.place(place_id)
            
            if result and result.get('status') == 'OK':
                place = result['result']
                return {
                    'name': place.get('name'),
                    'formatted_address': place.get('formatted_address'),
                    'phone': place.get('formatted_phone_number'),
                    'website': place.get('website'),
                    'rating': place.get('rating'),
                    'types': place.get('types', []),
                    'location': place.get('geometry', {}).get('location')
                }
            
            return None
            
        except Exception as e:
            print(f"Place details error: {e}")
            return None
