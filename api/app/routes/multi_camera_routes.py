from flask import Blueprint
from app.controllers.multi_camera_controller import (
    start_multi_camera_detection,
    stop_multi_camera_detection,
    get_detection_service_status,
    get_cameras_with_detection_status,
    force_detection_on_camera,
    restart_camera_detection,
    get_detection_statistics
)

# Create blueprint for multi-camera detection routes
multi_camera_bp = Blueprint('multi_camera', __name__)

# Detection service management routes
@multi_camera_bp.route('/detection/start', methods=['POST'])
def start_detection():
    """Start multi-camera detection service"""
    return start_multi_camera_detection()

@multi_camera_bp.route('/detection/stop', methods=['POST'])
def stop_detection():
    """Stop multi-camera detection service"""
    return stop_multi_camera_detection()

@multi_camera_bp.route('/detection/status', methods=['GET'])
def detection_status():
    """Get detection service status"""
    return get_detection_service_status()

@multi_camera_bp.route('/detection/statistics', methods=['GET'])
def detection_statistics():
    """Get detection statistics"""
    return get_detection_statistics()

# Camera-specific detection routes
@multi_camera_bp.route('/cameras', methods=['GET'])
def cameras_with_status():
    """Get all cameras with detection status"""
    return get_cameras_with_detection_status()

@multi_camera_bp.route('/cameras/<camera_id>/detect', methods=['POST'])
def force_camera_detection(camera_id):
    """Force detection on specific camera"""
    return force_detection_on_camera(camera_id)

@multi_camera_bp.route('/cameras/<camera_id>/restart', methods=['POST'])
def restart_camera(camera_id):
    """Restart detection for specific camera"""
    return restart_camera_detection(camera_id)
