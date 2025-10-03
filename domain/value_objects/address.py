"""Address value object."""

from typing import Optional


class Address:
    """Address value object."""
    
    def __init__(
        self,
        street: str,
        house: str,
        apartment: Optional[str] = None,
        entrance: Optional[str] = None,
        floor: Optional[str] = None,
        city: str = "Москва",
        postal_code: Optional[str] = None,
        coordinates: Optional[tuple[float, float]] = None,
    ):
        if not street or not house:
            raise ValueError("Street and house are required")
        
        self.street = street.strip()
        self.house = house.strip()
        self.apartment = apartment.strip() if apartment else None
        self.entrance = entrance.strip() if entrance else None
        self.floor = floor.strip() if floor else None
        self.city = city.strip()
        self.postal_code = postal_code.strip() if postal_code else None
        self.coordinates = coordinates
    
    @property
    def full_address(self) -> str:
        """Get full address string."""
        parts = [self.street, self.house]
        
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        
        if self.entrance:
            parts.append(f"подъезд {self.entrance}")
        
        if self.floor:
            parts.append(f"этаж {self.floor}")
        
        return ", ".join(parts)
    
    @property
    def short_address(self) -> str:
        """Get short address string."""
        parts = [self.street, self.house]
        
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        
        return ", ".join(parts)
    
    @property
    def has_coordinates(self) -> bool:
        """Check if address has coordinates."""
        return self.coordinates is not None
    
    @property
    def latitude(self) -> Optional[float]:
        """Get latitude coordinate."""
        return self.coordinates[0] if self.coordinates else None
    
    @property
    def longitude(self) -> Optional[float]:
        """Get longitude coordinate."""
        return self.coordinates[1] if self.coordinates else None
    
    def set_coordinates(self, latitude: float, longitude: float) -> None:
        """Set coordinates."""
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        
        self.coordinates = (latitude, longitude)
    
    def clear_coordinates(self) -> None:
        """Clear coordinates."""
        self.coordinates = None
    
    def __str__(self) -> str:
        return self.full_address
    
    def __repr__(self) -> str:
        return f"Address(street='{self.street}', house='{self.house}', apartment='{self.apartment}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Address):
            return False
        
        return (
            self.street == other.street
            and self.house == other.house
            and self.apartment == other.apartment
            and self.entrance == other.entrance
            and self.floor == other.floor
            and self.city == other.city
        )
    
    def __hash__(self) -> int:
        return hash((
            self.street,
            self.house,
            self.apartment,
            self.entrance,
            self.floor,
            self.city,
        ))