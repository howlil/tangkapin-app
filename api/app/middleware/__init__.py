from app import jwt
from app.services.auth_service import is_token_blacklisted, get_user_by_id

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    """Check if token is blacklisted."""
    return is_token_blacklisted(jwt_payload)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Load user from database when JWT token is used."""
    identity = jwt_data["sub"]
    return get_user_by_id(identity) 