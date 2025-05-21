from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app.services.ml_service import detect_weapon, process_detection, check_ml_service_status
from app.services.camera_service import get_camera_by_id
from app.schemas import DetectionSchema
from app.utils.validators import validate_json_payload, validate_uuid
from app.utils.error_handlers import ApiError
from marshmallow import ValidationError

@jwt_required()
def submit_for_detection():
    """Submit an image for weapon detection."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['image', 'camera_id'])
    if validation_error:
        return validation_error
    
    try:
        # Validate data with schema
        DetectionSchema().load(data)
        
        # Validate camera ID
        if not validate_uuid(data['camera_id']):
            return jsonify({'error': 'Invalid camera ID format'}), 400
        
        # Check camera accessibility
        user_id = None if current_user.role == 'admin' else current_user.id
        try:
            camera = get_camera_by_id(data['camera_id'], user_id)
        except ApiError as e:
            return jsonify({'error': e.message, 'details': e.details}), e.status_code
        
        # Send to ML service for detection
        detection_results = detect_weapon(data['image'], data['camera_id'])
        
        # Process detection results
        processing_results = process_detection(detection_results, data['camera_id'])
        
        return jsonify(processing_results), 200
    
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def check_ml_status():
    """Check ML service status."""
    try:
        status = check_ml_service_status()
        return jsonify(status), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code 