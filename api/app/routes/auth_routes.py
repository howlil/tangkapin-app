from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.auth_controller import AuthController

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login route for all roles (Owner, Admin, Officer)"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    response, status_code = AuthController.login(email, password)
    return jsonify(response), status_code

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user route (for testing)"""
    data = request.get_json()
    response, status_code = AuthController.register(data)
    return jsonify(response), status_code

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile route"""
    user_id = get_jwt_identity()
    response, status_code = AuthController.get_profile(user_id)
    return jsonify(response), status_code

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile route"""
    user_id = get_jwt_identity()
    data = request.get_json()
    response, status_code = AuthController.update_profile(user_id, data)
    return jsonify(response), status_code 