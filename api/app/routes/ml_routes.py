# app/routes/ml_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app.utils.response import success_response, error_response
from app.models import User

ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/detect', methods=['POST', 'OPTIONS'])
@cross_origin()
def detect_weapon():
    """Endpoint for weapon detection"""
    if request.method == 'OPTIONS':
        return success_response(message="OK")
        
    try:
        # JWT required for POST
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return error_response("Authorization required", 401)
            
        return success_response(
            message="ML detection endpoint (placeholder)",
            data={"status": "not_implemented"}
        )
    except Exception as e:
        return error_response(str(e), 500)

@ml_bp.route('/status', methods=['GET', 'OPTIONS'])
@cross_origin()
def ml_status():
    """Get ML service status"""
    if request.method == 'OPTIONS':
        return success_response(message="OK")
        
    return success_response(
        message="ML service status",
        data={"status": "operational"}
    ) 