from flask import jsonify, request, make_response

def success_response(message="Success", data=None, status_code=200):
    """
    Create a standardized success response
    
    Args:
        message (str): Success message
        data (dict): Optional data to include in response
        status_code (int): HTTP status code
        
    Returns:
        tuple: (response_json, status_code)
    """
    response = {
        "success": True,
        "message": message,
        "data": data if data is not None else {}
    }
    return jsonify(response), status_code

def error_response(message="An error occurred", status_code=400, errors=None):
    """
    Create a standardized error response
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        errors (dict): Optional dictionary of field-specific errors
        
    Returns:
        tuple: (response_json, status_code)
    """
    response = {
        "success": False,
        "message": message,
        "errors": errors if errors is not None else {}
    }
    return jsonify(response), status_code

def handle_options_request():
    """
    Handle OPTIONS requests for CORS preflight checks
    
    Returns:
        response: A response for OPTIONS preflight requests
    """
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    return None 