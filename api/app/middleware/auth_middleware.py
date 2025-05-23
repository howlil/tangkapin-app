from flask import jsonify
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from app.models import User
from app.utils.logger import logger
from functools import wraps

def jwt_middleware(app):
    """Configure JWT middleware"""
    jwt = JWTManager(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        """Return the user ID as the JWT identity"""
        return user_id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Look up a user from the database using JWT identity"""
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity, is_active=True).one_or_none()
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired token"""
        logger.logger.warning(f"Expired token used: {jwt_payload.get('sub')}")
        return jsonify({
            'error': 'Token telah kedaluwarsa',
            'code': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid token"""
        logger.logger.warning(f"Invalid token used: {error}")
        return jsonify({
            'error': 'Token tidak valid',
            'code': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing token"""
        logger.logger.warning(f"No token provided: {error}")
        return jsonify({
            'error': 'Otorisasi dibutuhkan',
            'code': 'authorization_required'
        }), 401
    
    @jwt.token_verification_failed_loader
    def verification_failed_callback(jwt_header, jwt_payload):
        """Handle token verification failure"""
        logger.logger.warning(f"Token verification failed: {jwt_payload.get('sub')}")
        return jsonify({
            'error': 'Verifikasi token gagal',
            'code': 'token_verification_failed'
        }), 401
    
    logger.logger.info("JWT middleware initialized")

# Role-based authorization decorators
def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            logger.logger.warning(f"Admin role required, but user has {claims.get('role')}")
            return jsonify({"error": "Admin role required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def officer_required(fn):
    """Decorator to require officer role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "officer" and claims.get("role") != "admin":
            logger.logger.warning(f"Officer role required, but user has {claims.get('role')}")
            return jsonify({"error": "Officer role required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def owner_required(fn):
    """Decorator to require owner role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "owner" and claims.get("role") != "admin":
            logger.logger.warning(f"Owner role required, but user has {claims.get('role')}")
            return jsonify({"error": "Owner role required"}), 403
        return fn(*args, **kwargs)
    return wrapper 