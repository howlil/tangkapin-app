"""
Middleware module for handling cross-cutting concerns.
"""

def register_middleware(app):
    """Register all middleware with the Flask app"""
    from app.middleware.auth_middleware import jwt_middleware
    from app.middleware.error_middleware import error_handlers
    from app.middleware.request_middleware import request_handlers
    
    # Register middleware
    jwt_middleware(app)
    error_handlers(app)
    request_handlers(app)
    
    app.logger.info('All middleware registered successfully') 