# app/helpers/jwt.py
import jwt
from datetime import datetime, timedelta
from flask import current_app
import os

def create_jwt_token(user_id, role):
    """
    Create a JWT token for authentication
    
    Args:
        user_id (str): The user ID
        role (str): The user role
        
    Returns:
        str: The JWT token
    """
    # Set token expiration (default 24 hours)
    now = datetime.utcnow()
    expires = now + timedelta(seconds=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600 * 24))
    
    # Create payload
    payload = {
        'sub': user_id,
        'role': role,
        'iat': now,
        'exp': expires
    }
    
    # Generate token
    token = jwt.encode(
        payload,
        current_app.config.get('JWT_SECRET_KEY'),
        algorithm=current_app.config.get('JWT_ALGORITHM', 'HS256')
    )
    
    return token

def decode_jwt_token(token):
    """
    Decode and validate JWT token
    
    Args:
        token (str): The JWT token to decode
        
    Returns:
        dict: The decoded payload
        
    Raises:
        ValueError: If the token is invalid or expired
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            current_app.config.get('JWT_SECRET_KEY'),
            algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')]
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    except Exception as e:
        raise ValueError(f"Token validation error: {str(e)}")

def refresh_jwt_token(current_token):
    """Refresh JWT token if it's still valid but close to expiry"""
    try:
        # Decode current token
        payload = decode_jwt_token(current_token)
        
        # Check if token is within refresh window (e.g., last 6 hours)
        exp_time = datetime.fromtimestamp(payload['exp'])
        time_until_exp = exp_time - datetime.utcnow()
        
        if time_until_exp < timedelta(hours=6):
            # Create new token with same payload but extended expiry
            user_id = payload['id']
            role = payload['role']
            additional_data = {k: v for k, v in payload.items() 
                             if k not in ['id', 'role', 'exp', 'iat']}
            
            return create_jwt_token(user_id, role, additional_data)
        
        return current_token
        
    except ValueError:
        raise ValueError("Cannot refresh invalid token")