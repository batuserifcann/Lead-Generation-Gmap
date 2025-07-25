"""
Input validation utilities for Business Lead Automation System
"""
import re
from typing import List, Tuple, Optional
from urllib.parse import urlparse

class InputValidator:
    """Utility class for validating various input types"""

    @staticmethod
    def validate_business_name(name: str) -> Tuple[bool, str]:
        """Validate business name"""
        if not name or not name.strip():
            return False, "Business name cannot be empty"

        if len(name.strip()) < 2:
            return False, "Business name must be at least 2 characters long"

        if len(name.strip()) > 100:
            return False, "Business name cannot exceed 100 characters"

        return True, ""

    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """Validate phone number (Turkish format)"""
        if not phone:
            return True, ""  # Optional field

        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)

        # Check various Turkish phone number formats
        patterns = [
            r'^\+90\d{10}$',  # +90XXXXXXXXXX
            r'^90\d{10}$',    # 90XXXXXXXXXX
            r'^0\d{10}$',     # 0XXXXXXXXXX
            r'^\d{10}$'       # XXXXXXXXXX
        ]

        valid = any(re.match(pattern, cleaned) for pattern in patterns)

        if not valid:
            return False, "Invalid phone number format. Use Turkish format (e.g., +905551234567)"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email address"""
        if not email:
            return True, ""  # Optional field

        email = email.strip().lower()

        # Basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            return False, "Invalid email format"

        if len(email) > 254:
            return False, "Email address too long"

        return True, ""

    @staticmethod
    def validate_website_url(url: str) -> Tuple[bool, str]:
        """Validate website URL"""
        if not url:
            return True, ""  # Optional field

        url = url.strip()

        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            parsed = urlparse(url)

            # Check if URL has valid components
            if not parsed.netloc:
                return False, "Invalid URL format"

            # Check for valid domain
            domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(domain_pattern, parsed.netloc):
                return False, "Invalid domain format"

            return True, ""

        except Exception:
            return False, "Invalid URL format"

    @staticmethod
    def validate_google_rating(rating: str) -> Tuple[bool, str]:
        """Validate Google rating"""
        if not rating:
            return True, ""  # Optional field

        try:
            rating_float = float(rating)

            if not (0 <= rating_float <= 5):
                return False, "Rating must be between 0 and 5"

            return True, ""

        except ValueError:
            return False, "Rating must be a valid number"

    @staticmethod
    def validate_search_parameters(industry: str, location: str, radius: str, max_results: str) -> Tuple[bool, List[str]]:
        """Validate search parameters"""
        errors = []

        # Industry validation
        if not industry or not industry.strip():
            errors.append("Industry/Business type is required")
        elif len(industry.strip()) < 2:
            errors.append("Industry must be at least 2 characters long")

        # Location validation
        if not location or not location.strip():
            errors.append("Location is required")
        elif len(location.strip()) < 2:
            errors.append("Location must be at least 2 characters long")

        # Radius validation
        try:
            radius_int = int(radius)
            if radius_int < 1 or radius_int > 50:
                errors.append("Search radius must be between 1 and 50 km")
        except ValueError:
            errors.append("Search radius must be a valid number")

        # Max results validation
        try:
            max_results_int = int(max_results)
            if max_results_int < 1 or max_results_int > 1000:
                errors.append("Max results must be between 1 and 1000")
        except ValueError:
            errors.append("Max results must be a valid number")

        return len(errors) == 0, errors

    @staticmethod
    def validate_rate_limiting_settings(message_delay: str, max_messages_hour: str) -> Tuple[bool, List[str]]:
        """Validate rate limiting settings"""
        errors = []

        # Message delay validation
        try:
            delay = int(message_delay)
            if delay < 10 or delay > 300:
                errors.append("Message delay must be between 10 and 300 seconds")
        except ValueError:
            errors.append("Message delay must be a valid number")

        # Max messages per hour validation
        try:
            max_messages = int(max_messages_hour)
            if max_messages < 1 or max_messages > 100:
                errors.append("Max messages per hour must be between 1 and 100")
        except ValueError:
            errors.append("Max messages per hour must be a valid number")

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations"""
        if not filename:
            return "untitled"

        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')

        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        return sanitized or "untitled"

    @staticmethod
    def validate_message_template(template: str) -> Tuple[bool, List[str]]:
        """Validate message template"""
        errors = []

        if not template or not template.strip():
            errors.append("Message template cannot be empty")
            return False, errors

        if len(template) > 1000:
            errors.append("Message template cannot exceed 1000 characters")

        # Check for required placeholders
        required_placeholders = ['{business_name}']
        for placeholder in required_placeholders:
            if placeholder not in template:
                errors.append(f"Template must include {placeholder} placeholder")

        # Check for valid placeholders
        valid_placeholders = [
            '{business_name}', '{location}', '{industry}', '{address}',
            '{phone}', '{email}', '{website}'
        ]

        # Find all placeholders in template
        placeholders = re.findall(r'\{[^}]+\}', template)

        for placeholder in placeholders:
            if placeholder not in valid_placeholders:
                errors.append(f"Invalid placeholder: {placeholder}")

        return len(errors) == 0, errors