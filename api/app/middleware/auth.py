from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, current_user

def admin_required():
    """Decorator to require admin role."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            
            if current_user.role != 'admin':
                return jsonify(error="Admin access required"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def role_required(roles):
    """Decorator to require specific roles.
    
    Args:
        roles: List of role names or single role name
    """
    if isinstance(roles, str):
        roles = [roles]
    
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            
            if current_user.role not in roles:
                return jsonify(error=f"Required role: {', '.join(roles)}"), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def owner_or_admin_required():
    """Decorator to require owner or admin role."""
    return role_required(['owner', 'admin'])

def officer_or_admin_required():
    """Decorator to require officer or admin role."""
    return role_required(['officer', 'admin']) 