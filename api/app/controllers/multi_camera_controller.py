from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app.services.multi_camera_detection_service import MultiCameraDetectionService
from app.services.camera_service import get_cameras, get_camera_by_id
from app.utils.error_handlers import ApiError
from app.utils.validators import validate_json_payload, validate_uuid
from app.schemas import CameraSchema
import threading

# Global instance of multi-camera service
multi_camera_service = None
service_lock = threading.Lock()

def get_multi_camera_service(app):
    """Get or create multi-camera detection service instance"""
    global multi_camera_service
    
    with service_lock:
        if multi_camera_service is None:
            multi_camera_service = MultiCameraDetectionService(app, max_workers=8)
        return multi_camera_service

@jwt_required()
def start_multi_camera_detection():
    """Start multi-camera detection service"""
    try:
        # Only admin can start/stop detection service
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
        
        from flask import current_app
        service = get_multi_camera_service(current_app)
        
        if service.start_service():
            return jsonify({
                'message': 'Multi-camera detection service started successfully',
                'status': 'running'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to start multi-camera detection service',
                'status': 'stopped'
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Error starting service: {str(e)}'}), 500

@jwt_required()
def stop_multi_camera_detection():
    """Stop multi-camera detection service"""
    try:
        # Only admin can start/stop detection service
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
        
        global multi_camera_service
        
        if multi_camera_service and multi_camera_service.is_running:
            if multi_camera_service.stop_service():
                return jsonify({
                    'message': 'Multi-camera detection service stopped successfully',
                    'status': 'stopped'
                }), 200
            else:
                return jsonify({
                    'error': 'Failed to stop multi-camera detection service'
                }), 500
        else:
            return jsonify({
                'message': 'Multi-camera detection service is not running',
                'status': 'stopped'
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Error stopping service: {str(e)}'}), 500

@jwt_required()
def get_detection_service_status():
    """Get status of multi-camera detection service"""
    try:
        global multi_camera_service
        
        if multi_camera_service is None:
            return jsonify({
                'service_status': 'not_initialized',
                'active_cameras': {},
                'total_cameras': 0
            }), 200
        
        # Get service status
        is_running = multi_camera_service.is_running
        active_cameras_status = multi_camera_service.get_active_cameras_status()
        
        return jsonify({
            'service_status': 'running' if is_running else 'stopped',
            'active_cameras': active_cameras_status,
            'total_cameras': len(active_cameras_status),
            'max_workers': multi_camera_service.max_workers
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error getting service status: {str(e)}'}), 500

@jwt_required()
def get_cameras_with_detection_status():
    """Get all cameras with their detection status"""
    try:
        # Get user permissions
        user_id = None if current_user.role == 'admin' else current_user.id
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # Get cameras
        cameras, total, current_page, items_per_page = get_cameras(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status,
            active_only=active_only
        )
        
        # Get detection service status
        global multi_camera_service
        active_cameras_status = {}
        service_running = False
        
        if multi_camera_service and multi_camera_service.is_running:
            service_running = True
            active_cameras_status = multi_camera_service.get_active_cameras_status()
        
        # Enhance camera data with detection status
        cameras_with_status = []
        for camera in cameras:
            camera_data = CameraSchema().dump(camera)
            camera_data['detection_status'] = {
                'is_being_monitored': camera.id in active_cameras_status,
                'service_running': service_running,
                'last_detection': active_cameras_status.get(camera.id, {}).get('last_detection'),
                'frame_count': active_cameras_status.get(camera.id, {}).get('frame_count', 0),
                'queue_size': active_cameras_status.get(camera.id, {}).get('queue_size', 0)
            }
            cameras_with_status.append(camera_data)
        
        return jsonify({
            'cameras': cameras_with_status,
            'detection_service': {
                'status': 'running' if service_running else 'stopped',
                'active_cameras_count': len(active_cameras_status),
                'total_monitored': len([c for c in cameras_with_status if c['detection_status']['is_being_monitored']])
            },
            'pagination': {
                'total': total,
                'page': current_page,
                'per_page': items_per_page,
                'pages': (total // items_per_page) + (1 if total % items_per_page > 0 else 0)
            }
        }), 200
        
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code
    except Exception as e:
        return jsonify({'error': f'Error retrieving cameras: {str(e)}'}), 500

@jwt_required()
def force_detection_on_camera(camera_id):
    """Force weapon detection on specific camera with uploaded image"""
    try:
        # Validate camera ID
        if not validate_uuid(camera_id):
            return jsonify({'error': 'Invalid camera ID format'}), 400
        
        # Get and validate request data
        data = request.get_json()
        validation_error = validate_json_payload(data, ['image'])
        if validation_error:
            return validation_error
        
        # Check camera access
        user_id = None if current_user.role == 'admin' else current_user.id
        camera = get_camera_by_id(camera_id, user_id)
        
        # Get detection service
        global multi_camera_service
        if not multi_camera_service:
            return jsonify({'error': 'Multi-camera detection service not initialized'}), 500
        
        # Force detection
        detection_results = multi_camera_service.force_detection_on_camera(
            camera_id, 
            data['image']
        )
        
        if detection_results is None:
            return jsonify({
                'message': 'Detection completed but no results returned',
                'camera_id': camera_id,
                'camera_name': camera.name
            }), 200
        
        return jsonify({
            'message': 'Forced detection completed successfully',
            'camera_id': camera_id,
            'camera_name': camera.name,
            'detection_results': detection_results
        }), 200
        
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code
    except Exception as e:
        return jsonify({'error': f'Error in forced detection: {str(e)}'}), 500

@jwt_required()
def restart_camera_detection(camera_id):
    """Restart detection for specific camera"""
    try:
        # Only admin can restart camera detection
        if current_user.role != 'admin':
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
        
        # Validate camera ID
        if not validate_uuid(camera_id):
            return jsonify({'error': 'Invalid camera ID format'}), 400
        
        # Check if camera exists and is accessible
        camera = get_camera_by_id(camera_id)
        
        # Get detection service
        global multi_camera_service
        if not multi_camera_service or not multi_camera_service.is_running:
            return jsonify({'error': 'Multi-camera detection service not running'}), 500
        
        # Stop and restart camera processing
        with multi_camera_service.lock:
            if camera_id in multi_camera_service.active_cameras:
                multi_camera_service._stop_camera_processing(camera_id)
            
            multi_camera_service._start_camera_processing(camera)
        
        return jsonify({
            'message': f'Detection restarted for camera: {camera.name}',
            'camera_id': camera_id,
            'camera_name': camera.name
        }), 200
        
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code
    except Exception as e:
        return jsonify({'error': f'Error restarting camera detection: {str(e)}'}), 500

@jwt_required()
def get_detection_statistics():
    """Get detection statistics across all cameras"""
    try:
        global multi_camera_service
        
        if not multi_camera_service or not multi_camera_service.is_running:
            return jsonify({
                'service_status': 'stopped',
                'statistics': {
                    'total_cameras': 0,
                    'active_cameras': 0,
                    'average_fps': 0,
                    'total_detections_today': 0
                }
            }), 200
        
        # Get basic statistics
        active_cameras_status = multi_camera_service.get_active_cameras_status()
        
        # Calculate statistics
        total_cameras = len(active_cameras_status)
        total_frames = sum(status.get('frame_count', 0) for status in active_cameras_status.values())
        average_fps = round(total_frames / max(total_cameras, 1) / 60, 2)  # Rough FPS estimate
        
        # Get detections count from database (today)
        from datetime import datetime, timedelta
        from app.models import Report
        
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        detections_today = Report.query.filter(
            Report.is_automatic == True,
            Report.created_at >= today_start,
            Report.created_at <= today_end
        ).count()
        
        return jsonify({
            'service_status': 'running',
            'statistics': {
                'total_cameras': total_cameras,
                'active_cameras': len([s for s in active_cameras_status.values() if s.get('frame_count', 0) > 0]),
                'average_fps': average_fps,
                'total_detections_today': detections_today,
                'cameras_detail': active_cameras_status
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error getting detection statistics: {str(e)}'}), 500
