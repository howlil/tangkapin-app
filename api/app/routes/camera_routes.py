from flask import Blueprint
from app.controllers.cameras import (
    get_all_cameras,
    get_camera,
    create_new_camera,
    update_camera_details,
    update_camera_status_endpoint,
    delete_camera_endpoint,
    get_camera_stream
)

camera_bp = Blueprint('cameras', __name__)

# Get all cameras (filtered by role)
@camera_bp.route('', methods=['GET'])
def get_cameras_route():
    """Get all cameras (filtered by role)."""
    return get_all_cameras()

# Get a specific camera
@camera_bp.route('/<camera_id>', methods=['GET'])
def get_camera_route(camera_id):
    """Get a camera by ID."""
    return get_camera(camera_id)

# Create a new camera
@camera_bp.route('', methods=['POST'])
def create_camera_route():
    """Create a new camera."""
    return create_new_camera()

# Update a camera
@camera_bp.route('/<camera_id>', methods=['PUT'])
def update_camera_route(camera_id):
    """Update a camera."""
    return update_camera_details(camera_id)

# Update camera status
@camera_bp.route('/<camera_id>/status', methods=['PUT'])
def update_status_route(camera_id):
    """Update a camera's status."""
    return update_camera_status_endpoint(camera_id)

# Delete a camera
@camera_bp.route('/<camera_id>', methods=['DELETE'])
def delete_camera_route(camera_id):
    """Delete a camera."""
    return delete_camera_endpoint(camera_id)

# Get secure stream URL
@camera_bp.route('/<camera_id>/stream', methods=['GET'])
def get_stream_route(camera_id):
    """Get a secure stream URL for the camera."""
    return get_camera_stream(camera_id) 