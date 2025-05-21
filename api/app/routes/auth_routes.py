from flask import Blueprint
from app.controllers.auth import (
    register, 
    login, 
    refresh, 
    logout, 
    me, 
    update_profile, 
    change_user_password
)
from app import limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register_route():
    """Register a new user."""
    return register()

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login_route():
    """Login a user."""
    return login()

@auth_bp.route('/refresh', methods=['POST'])
def refresh_route():
    """Refresh access token."""
    return refresh()

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    """Logout a user."""
    return logout()

@auth_bp.route('/me', methods=['GET'])
def me_route():
    """Get current user profile."""
    return me()

@auth_bp.route('/profile', methods=['PUT'])
def update_profile_route():
    """Update user profile."""
    return update_profile()

@auth_bp.route('/password', methods=['PUT'])
@limiter.limit("5 per minute")
def change_password_route():
    """Change user password."""
    return change_user_password() 