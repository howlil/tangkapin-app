"""
Multi-Camera Detection Configuration
"""
import os
from typing import Dict, Any

class MultiCameraConfig:
    """Configuration class for multi-camera detection service"""
    
    # Performance Settings
    MAX_WORKERS = int(os.getenv('MULTI_CAMERA_MAX_WORKERS', 8))
    FRAME_SKIP = int(os.getenv('MULTI_CAMERA_FRAME_SKIP', 3))
    DETECTION_INTERVAL = float(os.getenv('MULTI_CAMERA_DETECTION_INTERVAL', 2.0))
    MAX_QUEUE_SIZE = int(os.getenv('MULTI_CAMERA_MAX_QUEUE_SIZE', 10))
    
    # Camera Settings
    CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', 640))
    CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', 480))
    CAMERA_FPS = int(os.getenv('CAMERA_FPS', 15))
    CAMERA_BUFFER_SIZE = int(os.getenv('CAMERA_BUFFER_SIZE', 1))
    
    # Monitoring Settings
    CAMERA_MONITOR_INTERVAL = int(os.getenv('CAMERA_MONITOR_INTERVAL', 30))  # seconds
    SERVICE_HEALTH_CHECK_INTERVAL = int(os.getenv('SERVICE_HEALTH_CHECK_INTERVAL', 300))  # seconds
    
    # Detection Thresholds
    ML_CONFIDENCE_THRESHOLD = float(os.getenv('ML_CONFIDENCE_THRESHOLD', 0.70))
    MIN_DETECTION_SIZE = int(os.getenv('MIN_DETECTION_SIZE', 20))  # pixels
    
    # Retry and Error Handling
    MAX_CAMERA_RETRIES = int(os.getenv('MAX_CAMERA_RETRIES', 3))
    CAMERA_RETRY_DELAY = int(os.getenv('CAMERA_RETRY_DELAY', 5))  # seconds
    ERROR_COOLDOWN_PERIOD = int(os.getenv('ERROR_COOLDOWN_PERIOD', 60))  # seconds
    
    # Resource Limits
    MAX_MEMORY_USAGE_MB = int(os.getenv('MAX_MEMORY_USAGE_MB', 2048))
    MAX_CPU_USAGE_PERCENT = int(os.getenv('MAX_CPU_USAGE_PERCENT', 80))
    
    # Logging
    LOG_DETECTION_EVENTS = os.getenv('LOG_DETECTION_EVENTS', 'true').lower() == 'true'
    LOG_PERFORMANCE_METRICS = os.getenv('LOG_PERFORMANCE_METRICS', 'true').lower() == 'true'
    LOG_CAMERA_STATUS = os.getenv('LOG_CAMERA_STATUS', 'true').lower() == 'true'
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            'performance': {
                'max_workers': cls.MAX_WORKERS,
                'frame_skip': cls.FRAME_SKIP,
                'detection_interval': cls.DETECTION_INTERVAL,
                'max_queue_size': cls.MAX_QUEUE_SIZE
            },
            'camera': {
                'width': cls.CAMERA_WIDTH,
                'height': cls.CAMERA_HEIGHT,
                'fps': cls.CAMERA_FPS,
                'buffer_size': cls.CAMERA_BUFFER_SIZE
            },
            'monitoring': {
                'camera_monitor_interval': cls.CAMERA_MONITOR_INTERVAL,
                'service_health_check_interval': cls.SERVICE_HEALTH_CHECK_INTERVAL
            },
            'detection': {
                'confidence_threshold': cls.ML_CONFIDENCE_THRESHOLD,
                'min_detection_size': cls.MIN_DETECTION_SIZE
            },
            'error_handling': {
                'max_camera_retries': cls.MAX_CAMERA_RETRIES,
                'camera_retry_delay': cls.CAMERA_RETRY_DELAY,
                'error_cooldown_period': cls.ERROR_COOLDOWN_PERIOD
            },
            'resources': {
                'max_memory_mb': cls.MAX_MEMORY_USAGE_MB,
                'max_cpu_percent': cls.MAX_CPU_USAGE_PERCENT
            },
            'logging': {
                'detection_events': cls.LOG_DETECTION_EVENTS,
                'performance_metrics': cls.LOG_PERFORMANCE_METRICS,
                'camera_status': cls.LOG_CAMERA_STATUS
            }
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, str]:
        """Validate configuration and return any errors"""
        errors = {}
        
        if cls.MAX_WORKERS < 1:
            errors['max_workers'] = "Must be at least 1"
        
        if cls.FRAME_SKIP < 1:
            errors['frame_skip'] = "Must be at least 1"
        
        if cls.DETECTION_INTERVAL < 0.1:
            errors['detection_interval'] = "Must be at least 0.1 seconds"
        
        if cls.ML_CONFIDENCE_THRESHOLD < 0.1 or cls.ML_CONFIDENCE_THRESHOLD > 1.0:
            errors['confidence_threshold'] = "Must be between 0.1 and 1.0"
        
        if cls.CAMERA_WIDTH < 320 or cls.CAMERA_HEIGHT < 240:
            errors['camera_resolution'] = "Minimum resolution is 320x240"
        
        return errors

# Export configuration instance
multi_camera_config = MultiCameraConfig()
