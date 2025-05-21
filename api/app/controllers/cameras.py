from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app.services.camera_service import (
    get_cameras,
    get_camera_by_id,
    create_camera,
    update_camera,
    update_camera_status,
    delete_camera,
    get_secure_stream_url
)
from app.schemas import CameraSchema
from app.middleware.auth import owner_or_admin_required, admin_required
from app.utils.validators import validate_json_payload
from app.utils.error_handlers import ApiError

@jwt_required()
def get_all_cameras():
    """Get all cameras (filtered by role)."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        include_inactive = request.args.get('include_inactive', '').lower() in ['true', '1', 'yes']
        
        # Filter by owner for non-admin users
        user_id = None
        if current_user.role != 'admin':
            user_id = current_user.id
        
        # Get cameras
        cameras, total, current_page, items_per_page = get_cameras(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status,
            active_only=not include_inactive
        )
        
        # Serialize cameras
        camera_schema = CameraSchema(many=True)
        cameras_data = camera_schema.dump(cameras)
        
        return jsonify({
            'cameras': cameras_data,
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
def get_camera(camera_id):
    """Get a camera by ID."""
    try:
        # Get camera (automatically checks access rights for non-admin users)
        user_id = None if current_user.role == 'admin' else current_user.id
        camera = get_camera_by_id(camera_id, user_id)
        
        return jsonify(CameraSchema().dump(camera)), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
@owner_or_admin_required()
def create_new_camera():
    """Create a new camera."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['name', 'location', 'stream_url'])
    if validation_error:
        return validation_error
    
    try:
        # Create camera
        # If admin is creating for a specific owner, use that ID
        owner_id = data.get('owner_id') if current_user.role == 'admin' and 'owner_id' in data else current_user.id
        
        new_camera = create_camera(data, owner_id)
        
        return jsonify({
            'message': 'Camera created successfully',
            'camera': CameraSchema().dump(new_camera)
        }), 201
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def update_camera_details(camera_id):
    """Update a camera."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data)
    if validation_error:
        return validation_error
    
    try:
        # Get camera (automatically checks access rights for non-admin users)
        user_id = None if current_user.role == 'admin' else current_user.id
        camera = get_camera_by_id(camera_id, user_id)
        
        # Update camera
        updated_camera = update_camera(camera, data)
        
        return jsonify({
            'message': 'Camera updated successfully',
            'camera': CameraSchema().dump(updated_camera)
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def update_camera_status_endpoint(camera_id):
    """Update a camera's status."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['status'])
    if validation_error:
        return validation_error
    
    try:
        # Get camera (automatically checks access rights for non-admin users)
        user_id = None if current_user.role == 'admin' else current_user.id
        camera = get_camera_by_id(camera_id, user_id)
        
        # Update status
        updated_camera = update_camera_status(camera, data['status'])
        
        return jsonify({
            'message': f"Camera status updated to '{data['status']}'",
            'camera': CameraSchema().dump(updated_camera)
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def delete_camera_endpoint(camera_id):
    """Delete a camera."""
    try:
        # Get camera (automatically checks access rights for non-admin users)
        user_id = None if current_user.role == 'admin' else current_user.id
        camera = get_camera_by_id(camera_id, user_id)
        
        # Delete camera
        delete_camera(camera)
        
        return jsonify({
            'message': 'Camera deleted successfully'
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def get_camera_stream(camera_id):
    """Get a secure stream URL for the camera."""
    try:
        # Get camera (automatically checks access rights for non-admin users)
        user_id = None if current_user.role == 'admin' else current_user.id
        camera = get_camera_by_id(camera_id, user_id)
        
        # Get secure URL
        secure_url = get_secure_stream_url(camera)
        
        return jsonify({
            'stream_url': secure_url,
            'expires_at': None  # In a real implementation, this would be the expiration time
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code 