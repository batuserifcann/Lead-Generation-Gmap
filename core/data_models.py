"""
Data models for Business Lead Automation System
Defines business data structures and validation
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import re

@dataclass
class BusinessData:
    """Data class representing a business lead"""

    # Required fields
    business_name: str

    # Optional contact information
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    # Website analysis
    has_website: bool = False
    website_status: str = "Unknown"  # Unknown, Active, Inactive, Under Construction, No Website

    # Business details
    industry: Optional[str] = None
    location: Optional[str] = None
    google_rating: Optional[float] = None

    # Contact tracking
    contact_status: str = "Not Contacted"  # Not Contacted, Contacted, Responded, Interested, Not Interested
    last_contacted: Optional[str] = None
    notes: str = ""

    # System fields
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Validate and normalize data after initialization"""
        # Normalize business name
        if self.business_name:
            self.business_name = self.business_name.strip()

        # Normalize phone number
        if self.phone:
            self.phone = self.normalize_phone(self.phone)

        # Normalize email
        if self.email:
            self.email = self.email.strip().lower()

        # Normalize website URL
        if self.website:
            self.website = self.normalize_website_url(self.website)

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number format"""
        if not phone:
            return ""

        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)

        # Handle Turkish phone numbers
        if cleaned.startswith('0'):
            cleaned = '+90' + cleaned[1:]
        elif cleaned.startswith('90') and len(cleaned) == 12:
            cleaned = '+' + cleaned
        elif not cleaned.startswith('+'):
            # Assume Turkish number if no country code
            if len(cleaned) == 10:
                cleaned = '+90' + cleaned

        return cleaned

    @staticmethod
    def normalize_website_url(url: str) -> str:
        """Normalize website URL"""
        if not url:
            return ""

        url = url.strip().lower()

        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Remove trailing slash
        url = url.rstrip('/')

        return url

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Excel export"""
        return {
            'id': self.id,
            'business_name': self.business_name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'has_website': self.has_website,
            'website_status': self.website_status,
            'industry': self.industry,
            'location': self.location,
            'google_rating': self.google_rating,
            'contact_status': self.contact_status,
            'last_contacted': self.last_contacted,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusinessData':
        """Create BusinessData from dictionary"""
        return cls(
            id=data.get('id'),
            business_name=data.get('business_name', ''),
            address=data.get('address'),
            phone=data.get('phone'),
            email=data.get('email'),
            website=data.get('website'),
            has_website=bool(data.get('has_website', False)),
            website_status=data.get('website_status', 'Unknown'),
            industry=data.get('industry'),
            location=data.get('location'),
            google_rating=data.get('google_rating'),
            contact_status=data.get('contact_status', 'Not Contacted'),
            last_contacted=data.get('last_contacted'),
            notes=data.get('notes', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def is_valid(self) -> tuple[bool, list[str]]:
        """Validate the business data"""
        errors = []

        # Required field validation
        if not self.business_name or not self.business_name.strip():
            errors.append("Business name is required")

        # Phone validation
        if self.phone and not self.is_valid_phone(self.phone):
            errors.append("Invalid phone number format")

        # Email validation
        if self.email and not self.is_valid_email(self.email):
            errors.append("Invalid email format")

        # Website validation
        if self.website and not self.is_valid_website(self.website):
            errors.append("Invalid website URL format")

        # Rating validation
        if self.google_rating is not None:
            if not (0 <= self.google_rating <= 5):
                errors.append("Google rating must be between 0 and 5")

        return len(errors) == 0, errors

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return True  # Optional field

        # Turkish phone number pattern
        pattern = r'^\+90\d{10}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return True  # Optional field

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_website(website: str) -> bool:
        """Validate website URL format"""
        if not website:
            return True  # Optional field

        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        return bool(re.match(pattern, website))