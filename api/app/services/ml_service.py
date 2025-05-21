import os
import base64
import requests
import json
from flask import current_app
from app.utils.error_handlers import ApiError
from app.services.report_service import create_ml_report

def detect_weapon(image_data, camera_id):
    """Send image to ML service for weapon detection.
    
    Args:
        image_data: Base64 encoded image data
        camera_id: Camera ID where the image was captured
        
    Returns:
        Dictionary containing detection results
        
    Raises:
        ApiError: If detection fails
    """
    try:
        # Get ML service URL and API key from config
        ml_service_url = current_app.config.get('ML_SERVICE_URL')
        ml_service_api_key = current_app.config.get('ML_SERVICE_API_KEY')
        
        if not ml_service_url:
            raise ApiError('ML service URL not configured', 500)
        
        # Set up the request
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add API key if available
        if ml_service_api_key:
            headers['X-API-Key'] = ml_service_api_key
        
        # Prepare the request payload
        payload = {
            'image': image_data,
            'camera_id': camera_id
        }
        
        # Send request to ML service
        response = requests.post(
            f"{ml_service_url}/detect",
            headers=headers,
            json=payload,
            timeout=30  # 30-second timeout
        )
        
        # Handle response
        if response.status_code != 200:
            raise ApiError(f'ML service error: {response.text}', 500)
        
        # Parse response
        detection_results = response.json()
        
        return detection_results
    
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"ML service request error: {str(e)}")
        raise ApiError('Error connecting to ML service', 500)
    
    except Exception as e:
        current_app.logger.error(f"ML detection error: {str(e)}")
        if 'ApiError' in str(type(e)):
            raise e
        raise ApiError('Error processing detection', 500)

def process_detection(detection_results, camera_id):
    """Process weapon detection results and create a report if necessary.
    
    Args:
        detection_results: Dictionary containing detection results
        camera_id: Camera ID where the detection occurred
        
    Returns:
        Dictionary containing processing results
        
    Raises:
        ApiError: If processing fails
    """
    try:
        # Check if a weapon was detected
        if not detection_results.get('weapon_detected', False):
            return {
                'report_created': False,
                'weapon_detected': False,
                'message': 'No weapon detected'
            }
        
        # Check confidence threshold for report creation
        confidence = detection_results.get('confidence', 0.0)
        confidence_threshold = current_app.config.get('ML_CONFIDENCE_THRESHOLD', 0.70)
        
        if confidence < confidence_threshold:
            return {
                'report_created': False,
                'weapon_detected': True,
                'confidence': confidence,
                'message': f'Weapon detected but confidence {confidence:.2f} below threshold {confidence_threshold:.2f}'
            }
        
        # Prepare data for report creation
        report_data = {
            'confidence': confidence,
            'weapon_type': detection_results.get('weapon_type', 'Unknown'),
            'image_url': detection_results.get('image_url')
        }
        
        # Create report from detection
        report = create_ml_report(report_data, camera_id)
        
        return {
            'report_created': True,
            'report_id': report.id,
            'weapon_detected': True,
            'weapon_type': detection_results.get('weapon_type'),
            'confidence': confidence,
            'priority': report.priority,
            'message': f'Weapon detected with confidence {confidence:.2f}, report created'
        }
    
    except Exception as e:
        current_app.logger.error(f"Error processing detection: {str(e)}")
        if 'ApiError' in str(type(e)):
            raise e
        raise ApiError('Error processing detection results', 500)

def check_ml_service_status():
    """Check if ML service is available and responsive.
    
    Returns:
        Dictionary containing status information
        
    Raises:
        ApiError: If status check fails
    """
    try:
        # Get ML service URL from config
        ml_service_url = current_app.config.get('ML_SERVICE_URL')
        
        if not ml_service_url:
            return {
                'status': 'unavailable',
                'message': 'ML service URL not configured'
            }
        
        # Send status request to ML service
        response = requests.get(
            f"{ml_service_url}/status",
            timeout=5  # 5-second timeout
        )
        
        # Handle response
        if response.status_code != 200:
            return {
                'status': 'error',
                'message': f'ML service returned status code {response.status_code}'
            }
        
        # Parse response
        status_data = response.json()
        
        return {
            'status': 'online',
            'message': 'ML service is operational',
            'service_info': status_data
        }
    
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"ML service status check error: {str(e)}")
        return {
            'status': 'offline',
            'message': f'Error connecting to ML service: {str(e)}'
        }
    
    except Exception as e:
        current_app.logger.error(f"ML service status check error: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error checking ML service status: {str(e)}'
        } 