"""Phone value object."""

import re
from typing import Optional


class Phone:
    """Phone value object."""
    
    def __init__(self, phone: str):
        if not phone:
            raise ValueError("Phone cannot be empty")
        
        # Normalize phone number
        normalized = self._normalize_phone(phone)
        if not normalized:
            raise ValueError("Invalid phone number format")
        
        self.phone = normalized
    
    def _normalize_phone(self, phone: str) -> Optional[str]:
        """Normalize phone number to international format."""
        # Remove all non-digit characters
        clean_phone = re.sub(r'\D', '', phone)
        
        # Handle different formats
        if clean_phone.startswith('8') and len(clean_phone) == 11:
            # Russian format starting with 8
            clean_phone = '7' + clean_phone[1:]
        elif clean_phone.startswith('+7') and len(clean_phone) == 12:
            # International format
            clean_phone = clean_phone[1:]
        elif not clean_phone.startswith('7') and len(clean_phone) == 10:
            # Missing country code
            clean_phone = '7' + clean_phone
        
        # Validate final format
        if len(clean_phone) == 11 and clean_phone.startswith('7'):
            return clean_phone
        
        return None
    
    @property
    def formatted(self) -> str:
        """Get formatted phone number."""
        if len(self.phone) == 11:
            return f"+7 ({self.phone[1:4]}) {self.phone[4:7]}-{self.phone[7:9]}-{self.phone[9:11]}"
        return self.phone
    
    @property
    def international(self) -> str:
        """Get international format phone number."""
        return f"+{self.phone}"
    
    @property
    def national(self) -> str:
        """Get national format phone number."""
        if len(self.phone) == 11:
            return f"8 ({self.phone[1:4]}) {self.phone[4:7]}-{self.phone[7:9]}-{self.phone[9:11]}"
        return self.phone
    
    @property
    def digits_only(self) -> str:
        """Get phone number with digits only."""
        return self.phone
    
    @property
    def country_code(self) -> str:
        """Get country code."""
        return self.phone[:1] if self.phone else ""
    
    @property
    def area_code(self) -> str:
        """Get area code."""
        return self.phone[1:4] if len(self.phone) >= 4 else ""
    
    @property
    def number(self) -> str:
        """Get phone number without country and area codes."""
        return self.phone[4:] if len(self.phone) >= 4 else ""
    
    def is_mobile(self) -> bool:
        """Check if phone is mobile."""
        if len(self.phone) < 4:
            return False
        
        # Russian mobile codes
        mobile_codes = ['900', '901', '902', '903', '904', '905', '906', '908', '909',
                       '910', '911', '912', '913', '914', '915', '916', '917', '918', '919',
                       '920', '921', '922', '923', '924', '925', '926', '927', '928', '929',
                       '930', '931', '932', '933', '934', '936', '937', '938', '939',
                       '950', '951', '952', '953', '954', '955', '956', '958', '960',
                       '961', '962', '963', '964', '965', '966', '967', '968', '969',
                       '970', '971', '977', '978', '980', '981', '982', '983', '984', '985', '986', '987', '988', '989',
                       '991', '992', '993', '994', '995', '996', '997', '998', '999']
        
        return self.area_code in mobile_codes
    
    def __str__(self) -> str:
        return self.formatted
    
    def __repr__(self) -> str:
        return f"Phone(phone='{self.phone}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Phone):
            return False
        return self.phone == other.phone
    
    def __hash__(self) -> int:
        return hash(self.phone)