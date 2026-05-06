"""Yandex Maps provider implementation."""

import aiohttp
import json
from typing import Optional, Tuple, List, Dict

from domain.value_objects.address import Address
from infrastructure.external.maps.base_maps import BaseMapsProvider


class YandexMapsProvider(BaseMapsProvider):
    """Yandex Maps provider implementation."""
    
    def __init__(self, geocoder_api_key: str, suggest_api_key: Optional[str] = None):
        self.geocoder_api_key = geocoder_api_key
        self.suggest_api_key = suggest_api_key or geocoder_api_key
        self.base_url = "https://geocode-maps.yandex.ru/1.x"
        self.suggest_url = "https://suggest-maps.yandex.ru/v1/suggest"

    @staticmethod
    def _extract_suggest_text(value: object) -> str:
        """Normalize Yandex suggest title/subtitle to plain text."""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            text = value.get("text")
            if isinstance(text, str):
                return text.strip()
        return ""
    
    async def suggest_addresses(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """Get address suggestions using Yandex Suggest API."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "apikey": self.suggest_api_key,
                    "text": query,
                    "lang": "ru_RU",
                    "results": limit,
                    "type": "address"
                }
                
                async with session.get(self.suggest_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        suggestions = []
                        
                        if "results" in data:
                            for result in data["results"]:
                                title = self._extract_suggest_text(result.get("title"))
                                subtitle = self._extract_suggest_text(result.get("subtitle"))
                                if not title:
                                    continue

                                full_address = title if not subtitle else f"{title}, {subtitle}"
                                suggestions.append({
                                    "title": title,
                                    "subtitle": subtitle,
                                    "full_address": full_address,
                                    "coordinates": result.get("coordinates", {})
                                })
                        
                        return suggestions
                    else:
                        return []
        except Exception as e:
            print(f"Error getting address suggestions: {e}")
            return []

    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode address to coordinates using Yandex Maps."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "apikey": self.geocoder_api_key,
                    "geocode": address,
                    "format": "json",
                    "results": 1
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "response" in data and "GeoObjectCollection" in data["response"]:
                            geo_objects = data["response"]["GeoObjectCollection"]["featureMember"]
                            if geo_objects:
                                pos = geo_objects[0]["GeoObject"]["Point"]["pos"]
                                lon, lat = map(float, pos.split())
                                return (lat, lon)
                    
                    return None
        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """Reverse geocode coordinates to address using Yandex Maps."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "apikey": self.geocoder_api_key,
                    "geocode": f"{longitude},{latitude}",
                    "format": "json",
                    "results": 1
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "response" in data and "GeoObjectCollection" in data["response"]:
                            geo_objects = data["response"]["GeoObjectCollection"]["featureMember"]
                            if geo_objects:
                                return geo_objects[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["text"]
                    
                    return None
        except Exception as e:
            print(f"Error reverse geocoding: {e}")
            return None
    
    async def calculate_distance(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[float]:
        """Calculate distance between two points using Yandex Maps."""
        # Simple Euclidean distance calculation for now
        # In production, you might want to use Yandex Router API
        import math
        
        lat1, lon1 = origin
        lat2, lon2 = destination
        
        # Haversine formula for distance calculation
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    async def calculate_duration(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[int]:
        """Calculate travel duration between two points using Yandex Maps."""
        # Simple estimation: 1 minute per 500 meters
        distance = await self.calculate_distance(origin, destination)
        if distance:
            return int(distance / 500)  # minutes
        return None
    
    async def validate_delivery_zone(
        self,
        address: str,
        cafe_coordinates: Tuple[float, float],
        max_distance: float = 5000  # 5km default
    ) -> bool:
        """Validate if address is within delivery zone using Yandex Maps."""
        try:
            address_coords = await self.geocode_address(address)
            if not address_coords:
                return False
            
            distance = await self.calculate_distance(cafe_coordinates, address_coords)
            return distance is not None and distance <= max_distance
        except Exception as e:
            print(f"Error validating delivery zone: {e}")
            return False
    
    async def get_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[dict]:
        """Get route between two points using Yandex Maps."""
        # For now, return basic route info
        # In production, use Yandex Router API
        distance = await self.calculate_distance(origin, destination)
        duration = await self.calculate_duration(origin, destination)
        
        if distance and duration:
            return {
                "distance": distance,
                "duration": duration,
                "origin": origin,
                "destination": destination
            }
        return None
    
    async def get_map_url(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 15
    ) -> str:
        """Get Yandex Maps URL for coordinates."""
        return f"https://yandex.ru/maps/?ll={longitude},{latitude}&z={zoom}&l=map"