from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app.services.user_service import (
    get_users, 
    get_user_by_id, 
    deactivate_user,
    activate_user,
    delete_user
)
from app.services.auth_service import update_user
from app.schemas import UserSchema
from app.middleware.auth import admin_required
from app.utils.error_handlers import ApiError

@jwt_required()
@admin_required()
def get_all_users():
    """Get all users (admin only)."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role')
        include_inactive = request.args.get('include_inactive', '').lower() in ['true', '1', 'yes']
        
        # Get users
        users, total, current_page, items_per_page = get_users(
            page=page, 
            per_page=per_page, 
            role=role, 
            active_only=not include_inactive
        )
        
        # Serialize users
        user_schema = UserSchema(many=True)
        users_data = user_schema.dump(users)
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'total': total,
                'page': current_page,
                'per_page': items_per_page,
                'pages': (total // items_per_page) + (1 if total % items_per_page > 0 else 0)
            }
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code


@jwt_required()
@admin_required()
def get_user(user_id):
    """Get a user by ID (admin only)."""
    try:
        user = get_user_by_id(user_id)
        return jsonify(UserSchema().dump(user)), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code


@jwt_required()
@admin_required()
def update_user_details(user_id):
    """Update a user (admin only)."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        user = get_user_by_id(user_id)
        updated_user = update_user(user, data)
        return jsonify(UserSchema().dump(updated_user)), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code


@jwt_required()
@admin_required()
def deactivate_user_account(user_id):
    """Deactivate a user account (admin only)."""
    try:
        user = get_user_by_id(user_id)
        
        # Prevent deactivating the current user
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        updated_user = deactivate_user(user)
        return jsonify({
            'message': 'User deactivated successfully',
            'user': UserSchema().dump(updated_user)
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code


@jwt_required()
@admin_required()
def activate_user_account(user_id):
    """Activate a user account (admin only)."""
    try:
        user = get_user_by_id(user_id)
        updated_user = activate_user(user)
        return jsonify({
            'message': 'User activated successfully',
            'user': UserSchema().dump(updated_user)
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code


@jwt_required()
@admin_required()
def delete_user_account(user_id):
    """Delete a user account (admin only)."""
    try:
        user = get_user_by_id(user_id)
        
        # Prevent deleting the current user
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        delete_user(user)
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code 