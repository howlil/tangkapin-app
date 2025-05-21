from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    current_user
)
from marshmallow import ValidationError
from app.services.auth_service import (
    register_user, 
    authenticate_user, 
    blacklist_token,
    update_user,
    change_password
)
from app.schemas import RegisterSchema, LoginSchema, PasswordChangeSchema, UserSchema
from app.utils.validators import validate_json_payload
from app.utils.error_handlers import ApiError

def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['email', 'password', 'name', 'role'])
    if validation_error:
        return validation_error
    
    try:
        # Validate data with schema
        RegisterSchema().load(data)
        
        # Register user
        user = register_user(data)
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': UserSchema().dump(user)
        }), 201
    
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code


def login():
    """Login a user."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['email', 'password'])
    if validation_error:
        return validation_error
    
    try:
        # Validate data with schema
        LoginSchema().load(data)
        
        # Authenticate user
        user = authenticate_user(data['email'], data['password'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': UserSchema().dump(user)
        }), 200
    
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400


@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    
    return jsonify({
        'access_token': access_token
    }), 200


@jwt_required()
def logout():
    """Logout a user by blacklisting their token."""
    try:
        blacklist_token()
        return jsonify({'message': 'Successfully logged out'}), 200
    
    except ApiError as e:
        return jsonify({'error': e.message}), e.status_code


@jwt_required()
def me():
    """Get current user profile."""
    return jsonify(UserSchema().dump(current_user)), 200


@jwt_required()
def update_profile():
    """Update user profile."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data)
    if validation_error:
        return validation_error
    
    try:
        # Update user
        updated_user = update_user(current_user, data)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': UserSchema().dump(updated_user)
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code


@jwt_required()
def change_user_password():
    """Change user password."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['current_password', 'new_password'])
    if validation_error:
        return validation_error
    
    try:
        # Validate data with schema
        PasswordChangeSchema().load(data)
        
        # Change password
        change_password(current_user, data['current_password'], data['new_password'])
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
    
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code 