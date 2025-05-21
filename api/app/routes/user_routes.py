from flask import Blueprint
from app.controllers.users import (
    get_all_users,
    get_user,
    update_user_details,
    deactivate_user_account,
    activate_user_account,
    delete_user_account
)

user_bp = Blueprint('users', __name__)

@user_bp.route('', methods=['GET'])
def get_users_route():
    """Get all users (admin only)."""
    return get_all_users()

@user_bp.route('/<user_id>', methods=['GET'])
def get_user_route(user_id):
    """Get a user by ID (admin only)."""
    return get_user(user_id)

@user_bp.route('/<user_id>', methods=['PUT'])
def update_user_route(user_id):
    """Update a user (admin only)."""
    return update_user_details(user_id)

@user_bp.route('/<user_id>/deactivate', methods=['PUT'])
def deactivate_user_route(user_id):
    """Deactivate a user account (admin only)."""
    return deactivate_user_account(user_id)

@user_bp.route('/<user_id>/activate', methods=['PUT'])
def activate_user_route(user_id):
    """Activate a user account (admin only)."""
    return activate_user_account(user_id)

@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    """Delete a user account (admin only)."""
    return delete_user_account(user_id) 