from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.camera_controller import CameraController
from app.middleware.auth_middleware import admin_required, owner_required

# Create blueprint
cameras_bp = Blueprint('cameras', __name__)

@cameras_bp.route('', methods=['GET'])
@jwt_required()
def get_cameras():
    """Get all cameras, filtered by user if specified"""
    user_id = get_jwt_identity()
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    response, status_code = CameraController.get_all_cameras(user_id, active_only)
    return jsonify(response), status_code

@cameras_bp.route('/<camera_id>', methods=['GET'])
@jwt_required()
def get_camera(camera_id):
    """Get a specific camera by ID"""
    response, status_code = CameraController.get_camera_by_id(camera_id)
    return jsonify(response), status_code

@cameras_bp.route('', methods=['POST'])
@jwt_required()
def create_camera():
    """Create a new camera"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    response, status_code = CameraController.create_camera(data, user_id)
    return jsonify(response), status_code

@cameras_bp.route('/<camera_id>', methods=['PUT'])
@jwt_required()
def update_camera(camera_id):
    """Update a camera"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    response, status_code = CameraController.update_camera(camera_id, data, user_id)
    return jsonify(response), status_code

@cameras_bp.route('/<camera_id>', methods=['DELETE'])
@jwt_required()
def delete_camera(camera_id):
    """Delete a camera"""
    user_id = get_jwt_identity()
    
    response, status_code = CameraController.delete_camera(camera_id, user_id)
    return jsonify(response), status_code

@cameras_bp.route('/<camera_id>/status', methods=['PUT'])
@jwt_required()
def update_camera_status(camera_id):
    """Update camera status"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Status diperlukan'}), 400
        
    response, status_code = CameraController.update_camera_status(camera_id, data['status'], user_id)
    return jsonify(response), status_code 