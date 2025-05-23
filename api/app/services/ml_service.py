import os
import base64
import requests
import json
import cv2
import numpy as np
from datetime import datetime
from flask import current_app
from app.utils.logger import logger
from app.models import DetectionLog, db
from app.services.ml_detection import MLDetectionService

# Initialize ML detection service
ml_detection_service = MLDetectionService()

def detect_weapon(image_data, camera_id):
    """Detect weapon in base64 encoded image data.
    
    Args:
        image_data: Base64 encoded image data
        camera_id: Camera ID where the image was captured
        
    Returns:
        Dictionary containing detection results
        
    Raises:
        Exception: If detection fails
    """
    try:
        # Convert base64 to opencv frame
        if isinstance(image_data, str):
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            frame = image_data
            
        if frame is None:
            logger.logger.error("Failed to decode image data")
            return None
            
        # Use the existing ML detection service
        detection_result = ml_detection_service._detect_weapons_in_frame(frame)
        
        if detection_result:
            # Convert to expected format
            return {
                'weapon_detected': detection_result.get('weapon_detected', False),
                'confidence': detection_result.get('confidence', 0.0),
                'weapon_type': detection_result.get('weapon_type', 'Unknown'),
                'bounding_boxes': detection_result.get('bounding_boxes', []),
                'image_path': detection_result.get('image_path'),
                'timestamp': datetime.now().isoformat()
            }
        
        return None
        
    except Exception as e:
        logger.logger.error(f"ML detection error: {str(e)}")
        raise e

def process_detection(detection_results, camera_id):
    """Process weapon detection results and create a report if necessary.
    
    Args:
        detection_results: Dictionary containing detection results
        camera_id: Camera ID where the detection occurred
        
    Returns:
        Dictionary containing processing results
    """
    try:
        from app.services.ml_detection import MLDetectionService
        from app.models import Camera
        
        # Check if a weapon was detected
        if not detection_results or not detection_results.get('weapon_detected', False):
            return {
                'report_created': False,
                'weapon_detected': False,
                'message': 'No weapon detected'
            }
        
        # Check confidence threshold for report creation
        confidence = detection_results.get('confidence', 0.0)
        confidence_threshold = getattr(current_app.config, 'ML_CONFIDENCE_THRESHOLD', 0.70)
        
        if confidence < confidence_threshold:
            return {
                'report_created': False,
                'weapon_detected': True,
                'confidence': confidence,
                'message': f'Weapon detected but confidence {confidence:.2f} below threshold {confidence_threshold:.2f}'
            }
        
        # Get camera and create detection log
        camera = Camera.query.get(camera_id)
        if camera:
            # Log the detection
            detection_log = DetectionLog(
                camera_id=camera_id,
                status='detected',
                confidence_score=confidence,
                weapon_detected=detection_results.get('weapon_type'),
                detection_image_path=detection_results.get('image_path'),
                raw_output=detection_results,
                model_version=ml_detection_service.model_version
            )
            db.session.add(detection_log)
            
            # Create auto report if confidence is high enough
            if confidence >= confidence_threshold:
                report = ml_detection_service._create_auto_report(camera, detection_log, detection_results)
                db.session.commit()
                
                return {
                    'report_created': True,
                    'report_id': report.id if report else None,
                    'weapon_detected': True,
                    'weapon_type': detection_results.get('weapon_type'),
                    'confidence': confidence,
                    'message': f'Weapon detected with confidence {confidence:.2f}, report created'
                }
            
            db.session.commit()
        
        return {
            'report_created': False,
            'weapon_detected': True,
            'weapon_type': detection_results.get('weapon_type'),
            'confidence': confidence,
            'message': f'Weapon detected with confidence {confidence:.2f}'
        }
    
    except Exception as e:
        logger.logger.error(f"Error processing detection: {str(e)}")
        raise e

def check_ml_service_status():
    """Check ML service status.
    
    Returns:
        Dictionary containing service status
    """
    try:
        return {
            'status': 'operational',
            'model_loaded': ml_detection_service.model is not None,
            'model_version': ml_detection_service.model_version,
            'device': str(ml_detection_service.device),
            'confidence_threshold': ml_detection_service.confidence_threshold
        }
    except Exception as e:
        logger.logger.error(f"Error checking ML service status: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
