"""Base maps provider class."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple

from domain.value_objects.address import Address


class BaseMapsProvider(ABC):
    """Base class for maps providers."""
    
    @abstractmethod
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode address to coordinates."""
        pass
    
    @abstractmethod
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """Reverse geocode coordinates to address."""
        pass
    
    @abstractmethod
    async def calculate_distance(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[float]:
        """Calculate distance between two points in meters."""
        pass
    
    @abstractmethod
    async def calculate_duration(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[int]:
        """Calculate travel duration between two points in minutes."""
        pass
    
    @abstractmethod
    async def validate_delivery_zone(
        self,
        address: Address,
        cafe_coordinates: Tuple[float, float],
        max_distance: float
    ) -> bool:
        """Validate if address is within delivery zone."""
        pass
    
    @abstractmethod
    async def get_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[dict]:
        """Get route between two points."""
        pass
    
    @abstractmethod
    async def get_map_url(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 15
    ) -> str:
        """Get map URL for coordinates."""
        pass