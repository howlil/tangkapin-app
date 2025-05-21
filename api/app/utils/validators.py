from flask import jsonify
import re
from app.utils.error_handlers import ApiError

def validate_json_payload(data, required_fields=None):
    """Validate that the request contains JSON data and required fields.
    
    Args:
        data: The JSON data from the request
        required_fields: A list of required field names
        
    Returns:
        None if validation passes, otherwise a Flask response with an error message
    """
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'fields': missing_fields
            }), 400
    
    return None


def validate_email(email):
    """Validate email format.
    
    Args:
        email: The email string to validate
        
    Returns:
        True if valid, False otherwise
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_password_strength(password):
    """Validate password strength.
    
    Args:
        password: The password string to validate
        
    Returns:
        True if valid, False otherwise
    """
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit
    if len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'[0-9]', password):
        return False
    
    return True


def validate_uuid(uuid_string):
    """Validate that the string is a valid UUID.
    
    Args:
        uuid_string: The UUID string to validate
        
    Returns:
        True if valid, False otherwise
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, uuid_string.lower()))


def validate_pagination_params(page, per_page, max_per_page=100):
    """Validate pagination parameters.
    
    Args:
        page: The page number
        per_page: Number of items per page
        max_per_page: Maximum allowed items per page
        
    Returns:
        Tuple of (page, per_page) with default values applied if needed
    """
    try:
        page = int(page) if page is not None else 1
        per_page = int(per_page) if per_page is not None else 20
    except ValueError:
        raise ApiError('Invalid pagination parameters', 400)
    
    if page < 1:
        page = 1
    
    if per_page < 1:
        per_page = 20
    
    if per_page > max_per_page:
        per_page = max_per_page
    
    return page, per_page


def validate_coordinates(latitude, longitude):
    """Validate geographic coordinates.
    
    Args:
        latitude: The latitude value
        longitude: The longitude value
        
    Returns:
        True if valid, False otherwise
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        if lat < -90 or lat > 90:
            return False
        
        if lon < -180 or lon > 180:
            return False
        
        return True
    except (ValueError, TypeError):
        return False 