import cv2
import numpy as np
import threading
import time
import queue
import base64
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.models import Camera, Report, DetectionLog, db
from app.utils.logger import logger
from app.services.ml_service import detect_weapon, process_detection
from app.services.notification_service import NotificationService
from app.services.supabase_storage import SupabaseStorageService
from app.config.multi_camera_config import multi_camera_config
from app.utils.performance_monitor import PerformanceMonitor

class MultiCameraDetectionService:
    """Enhanced service for concurrent weapon detection from multiple camera feeds"""
      def __init__(self, app=None, max_workers=None):
        self.app = app
        self.max_workers = max_workers or multi_camera_config.MAX_WORKERS
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.active_cameras = {}  # {camera_id: camera_info}
        self.detection_queues = {}  # {camera_id: detection_queue}
        self.camera_errors = {}  # {camera_id: error_info}
        self.lock = threading.Lock()
        self.is_running = False
        self.notification_service = NotificationService()
        self.storage_service = SupabaseStorageService()
        self.performance_monitor = PerformanceMonitor()
        
        # Detection parameters from config
        self.frame_skip = multi_camera_config.FRAME_SKIP
        self.detection_interval = multi_camera_config.DETECTION_INTERVAL
        self.max_queue_size = multi_camera_config.MAX_QUEUE_SIZE
        self.camera_width = multi_camera_config.CAMERA_WIDTH
        self.camera_height = multi_camera_config.CAMERA_HEIGHT
        self.camera_fps = multi_camera_config.CAMERA_FPS
        self.camera_buffer_size = multi_camera_config.CAMERA_BUFFER_SIZE
        
        # Error recovery parameters
        self.max_retries = multi_camera_config.MAX_CAMERA_RETRIES
        self.retry_delay = multi_camera_config.CAMERA_RETRY_DELAY
        self.error_cooldown = multi_camera_config.ERROR_COOLDOWN_PERIOD
        
        # Performance limits
        self.max_memory_mb = multi_camera_config.MAX_MEMORY_USAGE_MB
        self.max_cpu_percent = multi_camera_config.MAX_CPU_USAGE_PERCENT
        
        # Statistics
        self.stats = {
            'total_detections': 0,
            'total_frames_processed': 0,
            'service_start_time': None,
            'cameras_processed': 0
        }
        
        logger.logger.info(f"MultiCameraDetectionService initialized with {self.max_workers} workers")
      def start_service(self):
        """Start the multi-camera detection service"""
        if self.is_running:
            logger.logger.warning("Multi-camera detection service already running")
            return False
        
        self.is_running = True
        self.stats['service_start_time'] = datetime.now()
        
        # Start performance monitoring
        self.performance_monitor.start_monitoring()
        
        # Start main monitoring thread
        monitoring_thread = threading.Thread(target=self._monitor_cameras, daemon=True)
        monitoring_thread.start()
        
        # Start performance monitoring thread
        performance_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        performance_thread.start()
        
        logger.logger.info("✅ Multi-camera detection service started")
        return True
    
    def stop_service(self):
        """Stop the multi-camera detection service"""
        self.is_running = False
        
        with self.lock:
            # Stop all camera processing
            for camera_id in list(self.active_cameras.keys()):
                self._stop_camera_processing(camera_id)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.logger.info("✅ Multi-camera detection service stopped")
        return True
    
    def _monitor_cameras(self):
        """Main monitoring loop to manage active cameras"""
        while self.is_running:
            try:
                with self.app.app_context():
                    # Get all active and online cameras
                    cameras = Camera.query.filter_by(
                        is_active=True,
                        status='online'
                    ).all()
                    
                    current_camera_ids = {camera.id for camera in cameras}
                    
                    with self.lock:
                        active_camera_ids = set(self.active_cameras.keys())
                        
                        # Start new cameras
                        new_cameras = current_camera_ids - active_camera_ids
                        for camera_id in new_cameras:
                            camera = next(c for c in cameras if c.id == camera_id)
                            self._start_camera_processing(camera)
                        
                        # Stop removed cameras
                        removed_cameras = active_camera_ids - current_camera_ids
                        for camera_id in removed_cameras:
                            self._stop_camera_processing(camera_id)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.logger.error(f"Error in camera monitoring: {e}")
                time.sleep(60)  # Longer sleep on error
      def _start_camera_processing(self, camera):
        """Start processing for a specific camera with error recovery"""
        try:
            camera_id = camera.id
            
            # Check if camera is in error cooldown
            if self._is_camera_in_cooldown(camera_id):
                logger.logger.info(f"Camera {camera_id} in error cooldown, skipping")
                return
            
            # Create detection queue for this camera
            self.detection_queues[camera_id] = queue.Queue(maxsize=self.max_queue_size)
            
            # Store camera info with retry tracking
            self.active_cameras[camera_id] = {
                'camera': camera,
                'last_detection': None,
                'frame_count': 0,
                'active': True,
                'future': None,
                'retry_count': 0,
                'last_error': None,
                'start_time': datetime.now(),
                'total_detections': 0,
                'total_frames': 0
            }
            
            # Submit camera processing task
            future = self.executor.submit(self._process_camera_stream_with_retry, camera)
            self.active_cameras[camera_id]['future'] = future
            
            self.stats['cameras_processed'] += 1
            logger.logger.info(f"🎥 Started processing camera {camera_id}: {camera.name}")
            
        except Exception as e:
            logger.logger.error(f"Error starting camera {camera.id}: {e}")
            self._record_camera_error(camera.id, str(e))
    
    def _stop_camera_processing(self, camera_id):
        """Stop processing for a specific camera"""
        try:
            if camera_id in self.active_cameras:
                # Mark as inactive
                self.active_cameras[camera_id]['active'] = False
                
                # Cancel future if running
                future = self.active_cameras[camera_id].get('future')
                if future and not future.done():
                    future.cancel()
                
                # Clean up
                del self.active_cameras[camera_id]
                if camera_id in self.detection_queues:
                    del self.detection_queues[camera_id]
                
                logger.logger.info(f"🛑 Stopped processing camera {camera_id}")
                
        except Exception as e:
            logger.logger.error(f"Error stopping camera {camera_id}: {e}")
    
    def _process_camera_stream(self, camera):
        """Process video stream from a single camera"""
        camera_id = camera.id
        stream_url = camera.stream_url
        
        logger.logger.info(f"🔍 Starting stream processing for camera {camera_id}")
        
        cap = None
        frame_count = 0
        last_detection_time = 0
        
        try:
            # Initialize video capture
            cap = cv2.VideoCapture(stream_url)
            if not cap.isOpened():
                logger.logger.error(f"Cannot open camera stream: {stream_url}")
                return
            
            # Set capture properties for performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            cap.set(cv2.CAP_PROP_FPS, self.camera_fps)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, self.camera_buffer_size)  # Reduce buffer for real-time
            
            while (self.is_running and 
                   camera_id in self.active_cameras and 
                   self.active_cameras[camera_id]['active']):
                
                ret, frame = cap.read()
                if not ret:
                    logger.logger.warning(f"Failed to read frame from camera {camera_id}")
                    time.sleep(1)
                    continue
                
                frame_count += 1
                current_time = time.time()
                
                # Skip frames for performance
                if frame_count % self.frame_skip != 0:
                    continue
                
                # Check detection interval
                if current_time - last_detection_time < self.detection_interval:
                    continue
                
                # Add frame to detection queue (non-blocking)
                try:
                    detection_queue = self.detection_queues.get(camera_id)
                    if detection_queue and not detection_queue.full():
                        # Convert frame to base64 for detection API
                        frame_data = self._frame_to_base64(frame)
                        detection_queue.put({
                            'frame_data': frame_data,
                            'timestamp': current_time,
                            'camera_id': camera_id
                        }, block=False)
                        
                        # Process detection in separate thread
                        threading.Thread(
                            target=self._process_detection_queue,
                            args=(camera_id,),
                            daemon=True
                        ).start()
                        
                        last_detection_time = current_time
                        
                except queue.Full:
                    logger.logger.warning(f"Detection queue full for camera {camera_id}")
                    continue
                
                # Update camera info
                with self.lock:
                    if camera_id in self.active_cameras:
                        self.active_cameras[camera_id]['frame_count'] = frame_count
            
        except Exception as e:
            logger.logger.error(f"Error processing camera {camera_id}: {e}")
        
        finally:
            if cap:
                cap.release()
            logger.logger.info(f"🔚 Finished processing camera {camera_id}")
    
    def _process_detection_queue(self, camera_id):
        """Process detection queue for a specific camera"""
        try:
            detection_queue = self.detection_queues.get(camera_id)
            if not detection_queue or detection_queue.empty():
                return
            
            # Get frame data from queue
            frame_info = detection_queue.get_nowait()
            
            with self.app.app_context():
                # Send to ML detection service
                detection_results = detect_weapon(
                    frame_info['frame_data'],
                    frame_info['camera_id']
                )
                
                # Process detection results
                if detection_results:
                    processing_results = process_detection(
                        detection_results,
                        frame_info['camera_id']
                    )
                    
                    # Update last detection time
                    with self.lock:
                        if camera_id in self.active_cameras:
                            self.active_cameras[camera_id]['last_detection'] = datetime.now()
                    
                    # Log successful detection
                    if processing_results.get('weapon_detected'):
                        logger.logger.info(
                            f"🚨 Weapon detected on camera {camera_id}: "
                            f"{processing_results.get('weapon_type')} "
                            f"(confidence: {processing_results.get('confidence', 0):.2f})"
                        )
        
        except queue.Empty:
            pass
        except Exception as e:
            logger.logger.error(f"Error processing detection for camera {camera_id}: {e}")
    
    def _frame_to_base64(self, frame):
        """Convert OpenCV frame to base64 string"""
        try:
            import base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
        except Exception as e:
            logger.logger.error(f"Error converting frame to base64: {e}")
            return None
    
    def get_active_cameras_status(self):
        """Get status of all active cameras"""
        with self.lock:
            status = {}
            for camera_id, info in self.active_cameras.items():
                status[camera_id] = {
                    'name': info['camera'].name,
                    'location': info['camera'].location,
                    'frame_count': info.get('frame_count', 0),
                    'last_detection': info.get('last_detection'),
                    'queue_size': self.detection_queues.get(camera_id, queue.Queue()).qsize()
                }
            return status
    
    def force_detection_on_camera(self, camera_id, image_data):
        """Force detection on specific camera with provided image data"""
        try:
            with self.app.app_context():
                detection_results = detect_weapon(image_data, camera_id)
                if detection_results:
                    return process_detection(detection_results, camera_id)
                return None
        except Exception as e:
            logger.logger.error(f"Error in forced detection for camera {camera_id}: {e}")
            return None
    
    def _monitor_performance(self):
        """Monitor system performance and throttle if necessary"""
        while self.is_running:
            try:
                # Get current performance metrics
                metrics = self.performance_monitor.get_current_metrics()
                
                # Check memory usage
                if metrics.get('memory_usage_mb', 0) > self.max_memory_mb:
                    logger.logger.warning(f"High memory usage: {metrics['memory_usage_mb']}MB")
                    self._throttle_processing()
                
                # Check CPU usage
                if metrics.get('cpu_usage_percent', 0) > self.max_cpu_percent:
                    logger.logger.warning(f"High CPU usage: {metrics['cpu_usage_percent']}%")
                    self._throttle_processing()
                
                # Log performance metrics if enabled
                if multi_camera_config.LOG_PERFORMANCE_METRICS:
                    logger.logger.info(f"Performance: CPU {metrics.get('cpu_usage_percent', 0):.1f}%, "
                                     f"Memory {metrics.get('memory_usage_mb', 0):.1f}MB, "
                                     f"Active cameras: {len(self.active_cameras)}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.logger.error(f"Error in performance monitoring: {e}")
                time.sleep(60)
    
    def _throttle_processing(self):
        """Throttle processing when system resources are high"""
        with self.lock:
            # Increase frame skip rate temporarily
            original_frame_skip = self.frame_skip
            self.frame_skip = min(self.frame_skip * 2, 8)
            
            # Increase detection interval
            original_interval = self.detection_interval
            self.detection_interval = min(self.detection_interval * 1.5, 10.0)
            
            logger.logger.info(f"Throttling: frame_skip {original_frame_skip}->{self.frame_skip}, "
                             f"interval {original_interval:.1f}->{self.detection_interval:.1f}s")
            
            # Reset after 60 seconds
            def reset_throttle():
                time.sleep(60)
                with self.lock:
                    self.frame_skip = original_frame_skip
                    self.detection_interval = original_interval
                    logger.logger.info("Performance throttling reset")
            
            threading.Thread(target=reset_throttle, daemon=True).start()
    
    def _is_camera_in_cooldown(self, camera_id):
        """Check if camera is in error cooldown period"""
        if camera_id not in self.camera_errors:
            return False
        
        error_info = self.camera_errors[camera_id]
        cooldown_end = error_info['last_error_time'] + timedelta(seconds=self.error_cooldown)
        return datetime.now() < cooldown_end
    
    def _record_camera_error(self, camera_id, error_message):
        """Record camera error for tracking and cooldown"""
        if camera_id not in self.camera_errors:
            self.camera_errors[camera_id] = {
                'error_count': 0,
                'last_error_time': None,
                'last_error_message': None
            }
        
        self.camera_errors[camera_id].update({
            'error_count': self.camera_errors[camera_id]['error_count'] + 1,
            'last_error_time': datetime.now(),
            'last_error_message': error_message
        })
        
        logger.logger.error(f"Camera {camera_id} error #{self.camera_errors[camera_id]['error_count']}: {error_message}")
    
    def _process_camera_stream_with_retry(self, camera):
        """Process camera stream with automatic retry on failure"""
        camera_id = camera.id
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.logger.info(f"🔍 Processing camera {camera_id}, attempt {attempt + 1}")
                result = self._process_camera_stream(camera)
                
                # If successful, clear error tracking
                if camera_id in self.camera_errors:
                    del self.camera_errors[camera_id]
                
                return result
                
            except Exception as e:
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                self._record_camera_error(camera_id, error_msg)
                
                with self.lock:
                    if camera_id in self.active_cameras:
                        self.active_cameras[camera_id]['retry_count'] = attempt + 1
                        self.active_cameras[camera_id]['last_error'] = error_msg
                
                if attempt < self.max_retries:
                    logger.logger.warning(f"Retrying camera {camera_id} in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.logger.error(f"Camera {camera_id} failed after {self.max_retries + 1} attempts")
                    self._record_camera_error(camera_id, f"Max retries exceeded: {str(e)}")
                    break
