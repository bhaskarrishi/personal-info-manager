"""
Input validation utilities for the application.
"""
import re
from datetime import datetime
from typing import Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not email:
        return False, "Email is required"
    
    email = email.strip()
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 100:
        return False, "Email is too long (max 100 characters)"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username.
    
    Args:
        username: Username to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not username:
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username is too long (max 50 characters)"
    
    # Username should contain only alphanumeric characters and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, ""


def get_password_strength(password: str) -> str:
    """
    Get password strength rating.
    
    Args:
        password: Password to evaluate
    
    Returns:
        str: Strength rating ('Weak', 'Medium', 'Strong', 'Very Strong')
    """
    if not password:
        return "Weak"
    
    score = 0
    
    # Length check
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character variety checks
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    elif score <= 6:
        return "Strong"
    else:
        return "Very Strong"


def validate_required(value: str, field_name: str) -> Tuple[bool, str]:
    """
    Validate that a field is not empty.
    
    Args:
        value: Value to check
        field_name: Name of the field for error message
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not value or not str(value).strip():
        return False, f"{field_name} is required"
    return True, ""


def validate_date(date_str: str) -> Tuple[bool, str]:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not date_str:
        return True, ""  # Allow empty dates
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, "Invalid date format (use YYYY-MM-DD)"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not phone:
        return True, ""  # Allow empty phone
    
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it contains only digits and + (for country code)
    if not re.match(r'^\+?\d{7,15}$', phone):
        return False, "Invalid phone number format"
    
    return True, ""


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not url:
        return True, ""  # Allow empty URLs
    
    # Basic URL pattern
    pattern = r'^https?://[^\s/$.?#].[^\s]*$|^[^\s/$.?#].[^\s]*\.[^\s]{2,}$'
    
    if not re.match(pattern, url, re.IGNORECASE):
        return False, "Invalid URL format"
    
    return True, ""


def validate_number(value: str, field_name: str, min_val: float = None, max_val: float = None) -> Tuple[bool, str]:
    """
    Validate numeric value.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error message
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not value:
        return True, ""  # Allow empty numbers
    
    try:
        num = float(value)
        
        if min_val is not None and num < min_val:
            return False, f"{field_name} must be at least {min_val}"
        
        if max_val is not None and num > max_val:
            return False, f"{field_name} must not exceed {max_val}"
        
        return True, ""
    except ValueError:
        return False, f"{field_name} must be a valid number"


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful characters.
    
    Args:
        text: Text to sanitize
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text
