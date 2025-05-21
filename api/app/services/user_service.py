from flask import current_app
from app import db
from app.models import User
from app.utils.error_handlers import ApiError
from app.utils.validators import validate_pagination_params
from app.utils.validators import validate_uuid


def get_users(page=None, per_page=None, role=None, active_only=True):
    """Get a paginated list of users.
    
    Args:
        page: Page number
        per_page: Number of items per page
        role: Filter by role
        active_only: Only return active users
    
    Returns:
        Tuple of (users, total, page, per_page)
    """
    try:
        # Validate pagination parameters
        page, per_page = validate_pagination_params(page, per_page)
        
        # Build query
        query = User.query
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return users.items, total, page, per_page
    
    except Exception as e:
        current_app.logger.error(f"Error getting users: {str(e)}")
        raise ApiError('Error retrieving users', 500)


def get_user_by_id(user_id):
    """Get a user by ID.
    
    Args:
        user_id: The user ID
    
    Returns:
        User instance
    
    Raises:
        ApiError: If user not found
    """
    if not validate_uuid(user_id):
        raise ApiError('Invalid user ID format', 400)
    
    user = User.query.get(user_id)
    if not user:
        raise ApiError('User not found', 404)
    
    return user


def deactivate_user(user):
    """Deactivate a user.
    
    Args:
        user: User instance
    
    Returns:
        Updated user instance
    
    Raises:
        ApiError: If user cannot be deactivated
    """
    try:
        user.is_active = False
        db.session.commit()
        return user
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deactivating user: {str(e)}")
        raise ApiError('Error deactivating user', 500)


def activate_user(user):
    """Activate a user.
    
    Args:
        user: User instance
    
    Returns:
        Updated user instance
    
    Raises:
        ApiError: If user cannot be activated
    """
    try:
        user.is_active = True
        db.session.commit()
        return user
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error activating user: {str(e)}")
        raise ApiError('Error activating user', 500)


def delete_user(user):
    """Permanently delete a user.
    
    Args:
        user: User instance
    
    Returns:
        True if deleted
    
    Raises:
        ApiError: If user cannot be deleted
    """
    try:
        db.session.delete(user)
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        raise ApiError('Error deleting user - may have related records', 500) 