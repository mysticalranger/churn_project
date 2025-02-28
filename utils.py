import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?[0-9]{10,15}$'
    return re.match(pattern, phone) is not None

def format_date(date_str, input_format='%Y-%m-%d', output_format='%d %b %Y'):
    """Format date string from one format to another"""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError as e:
        logger.error(f"Date formatting error: {e}")
        return date_str

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def handle_error(error, message="An error occurred"):
    """Handle and log errors"""
    logger.error(f"{message}: {error}")
    return {"error": message, "details": str(error)}

def is_valid_date(date_str, date_format='%Y-%m-%d'):
    """Check if a date string is valid"""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False

def format_currency(amount):
    """Format currency value"""
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return str(amount)

def validate_number(value, min_val=None, max_val=None):
    """Validate numeric value"""
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    # Test utility functions
    print("Email validation:", validate_email("test@example.com"))
    print("Phone validation:", validate_phone("1234567890"))
    print("Date formatting:", format_date("2023-01-01"))
    print("Password validation:", validate_password("Password123"))
