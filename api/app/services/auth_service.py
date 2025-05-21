import uuid
from datetime import datetime
from flask import current_app
from flask_jwt_extended import get_jwt
from app import db
from app.models import User, TokenBlacklist
from app.utils.validators import validate_email, validate_password_strength
from app.utils.error_handlers import ApiError

def register_user(data):
    """Register a new user.
    
    Args:
        data: Dictionary containing user registration data
        
    Returns:
        The created User instance
        
    Raises:
        ApiError: If registration fails due to validation or other errors
    """
    # Validate email
    if not validate_email(data['email']):
        raise ApiError('Invalid email format', 400)
    
    # Check if email is already registered
    if User.query.filter_by(email=data['email']).first():
        raise ApiError('Email already registered', 400)
    
    # Validate password strength
    if not validate_password_strength(data['password']):
        raise ApiError('Password must be at least 8 characters and include uppercase, lowercase, and numbers', 400)
    
    # Validate role
    valid_roles = ['admin', 'officer', 'owner']
    if data['role'] not in valid_roles:
        raise ApiError(f'Role must be one of: {", ".join(valid_roles)}', 400)
    
    # Create user
    try:
        new_user = User(
            id=str(uuid.uuid4()),
            email=data['email'],
            name=data['name'],
            role=data['role'],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Set optional fields if provided
        if 'phone' in data:
            new_user.phone = data['phone']
        
        if 'address' in data:
            new_user.address = data['address']
        
        if 'badge_number' in data and data['role'] == 'officer':
            new_user.badge_number = data['badge_number']
        
        # Set password
        new_user.set_password(data['password'])
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        return new_user
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error registering user: {str(e)}")
        raise ApiError('Error registering user', 500)


def authenticate_user(email, password):
    """Authenticate a user with email and password.
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        User instance if authentication successful, None otherwise
    """
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return None
    
    if not user.is_active:
        return None
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return user


def blacklist_token():
    """Add the current access token to the blacklist.
    
    Returns:
        True if token was blacklisted successfully
    
    Raises:
        ApiError: If blacklisting fails
    """
    try:
        jwt_data = get_jwt()
        jti = jwt_data['jti']
        token_type = jwt_data['type']
        user_id = jwt_data['sub']
        exp = datetime.fromtimestamp(jwt_data['exp'])
        
        token_blacklist = TokenBlacklist(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            revoked=True,
            expires=exp,
            created_at=datetime.utcnow()
        )
        
        db.session.add(token_blacklist)
        db.session.commit()
        
        return True
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error blacklisting token: {str(e)}")
        raise ApiError('Error logging out', 500)


def is_token_blacklisted(jwt_payload):
    """Check if a token is blacklisted.
    
    Args:
        jwt_payload: The JWT payload
        
    Returns:
        True if token is blacklisted, False otherwise
    """
    jti = jwt_payload['jti']
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return bool(token and token.revoked)


def get_user_by_id(user_id):
    """Get a user by ID.
    
    Args:
        user_id: The user ID
        
    Returns:
        User instance if found, None otherwise
    """
    return User.query.get(user_id)


def update_user(user, data):
    """Update a user's information.
    
    Args:
        user: The User instance to update
        data: Dictionary containing update data
        
    Returns:
        The updated User instance
        
    Raises:
        ApiError: If update fails
    """
    try:
        # Update fields if provided
        if 'name' in data:
            user.name = data['name']
        
        if 'phone' in data:
            user.phone = data['phone']
        
        if 'address' in data:
            user.address = data['address']
        
        if 'badge_number' in data and user.role == 'officer':
            user.badge_number = data['badge_number']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return user
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user: {str(e)}")
        raise ApiError('Error updating user', 500)


def change_password(user, current_password, new_password):
    """Change a user's password.
    
    Args:
        user: The User instance
        current_password: The current password
        new_password: The new password
        
    Returns:
        True if password was changed successfully
        
    Raises:
        ApiError: If password change fails
    """
    # Verify current password
    if not user.check_password(current_password):
        raise ApiError('Current password is incorrect', 400)
    
    # Validate new password strength
    if not validate_password_strength(new_password):
        raise ApiError('New password must be at least 8 characters and include uppercase, lowercase, and numbers', 400)
    
    try:
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error changing password: {str(e)}")
        raise ApiError('Error changing password', 500)


def delete_user(user):
    """Delete a user.
    
    Args:
        user: The User instance to delete
        
    Returns:
        True if user was deleted successfully
        
    Raises:
        ApiError: If deletion fails
    """
    try:
        db.session.delete(user)
        db.session.commit()
        
        return True
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        raise ApiError('Error deleting user', 500) 