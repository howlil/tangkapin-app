import psutil
import time
from datetime import datetime, timedelta
from threading import Thread, Lock
from collections import defaultdict, deque
from app.utils.logger import logger

class MultiCameraPerformanceMonitor:
    """Monitor performance metrics for multi-camera detection service"""
    
    def __init__(self, service=None, history_size=100):
        self.service = service
        self.history_size = history_size
        self.metrics_history = defaultdict(lambda: deque(maxlen=history_size))
        self.lock = Lock()
        self.monitoring = False
        self.monitor_thread = None
        
        # Performance counters
        self.total_frames_processed = 0
        self.total_detections = 0
        self.detection_errors = 0
        self.camera_errors = defaultdict(int)
        
        # Timing metrics
        self.start_time = None
        self.last_reset_time = None
    
    def start_monitoring(self, interval=30):
        """Start performance monitoring"""
        if self.monitoring:
            logger.logger.warning("Performance monitoring already running")
            return
        
        self.monitoring = True
        self.start_time = datetime.now()
        self.last_reset_time = self.start_time
        
        self.monitor_thread = Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
        
        logger.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self, interval):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._collect_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.logger.error(f"Error in performance monitoring: {e}")
                time.sleep(60)  # Longer sleep on error
    
    def _collect_metrics(self):
        """Collect current performance metrics"""
        current_time = datetime.now()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        memory_used_mb = memory_info.used / (1024 * 1024)
        
        # Service metrics
        active_cameras = 0
        total_queue_size = 0
        camera_details = {}
        
        if self.service and hasattr(self.service, 'active_cameras'):
            with self.service.lock:
                active_cameras = len(self.service.active_cameras)
                
                for camera_id, info in self.service.active_cameras.items():
                    queue_size = 0
                    if camera_id in self.service.detection_queues:
                        queue_size = self.service.detection_queues[camera_id].qsize()
                        total_queue_size += queue_size
                    
                    camera_details[camera_id] = {
                        'frame_count': info.get('frame_count', 0),
                        'queue_size': queue_size,
                        'last_detection': info.get('last_detection'),
                        'active': info.get('active', False)
                    }
        
        # Calculate rates
        elapsed_seconds = (current_time - self.start_time).total_seconds()
        fps_total = self.total_frames_processed / max(elapsed_seconds, 1)
        detection_rate = self.total_detections / max(elapsed_seconds, 1) * 3600  # per hour
        error_rate = self.detection_errors / max(elapsed_seconds, 1) * 3600  # per hour
        
        # Store metrics
        with self.lock:
            self.metrics_history['timestamp'].append(current_time)
            self.metrics_history['cpu_percent'].append(cpu_percent)
            self.metrics_history['memory_percent'].append(memory_percent)
            self.metrics_history['memory_used_mb'].append(memory_used_mb)
            self.metrics_history['active_cameras'].append(active_cameras)
            self.metrics_history['total_queue_size'].append(total_queue_size)
            self.metrics_history['fps_total'].append(fps_total)
            self.metrics_history['detection_rate'].append(detection_rate)
            self.metrics_history['error_rate'].append(error_rate)
            self.metrics_history['camera_details'].append(camera_details)
        
        # Log high-level metrics
        logger.logger.info(
            f"Performance: CPU {cpu_percent:.1f}%, "
            f"Memory {memory_percent:.1f}% ({memory_used_mb:.0f}MB), "
            f"Cameras {active_cameras}, "
            f"Queue {total_queue_size}, "
            f"FPS {fps_total:.1f}, "
            f"Detections/hr {detection_rate:.1f}"
        )
        
        # Check for performance issues
        self._check_performance_alerts(cpu_percent, memory_percent, total_queue_size)
    
    def _check_performance_alerts(self, cpu_percent, memory_percent, queue_size):
        """Check for performance issues and log alerts"""
        from app.config.multi_camera_config import multi_camera_config
        
        alerts = []
        
        if cpu_percent > multi_camera_config.MAX_CPU_USAGE_PERCENT:
            alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        if memory_percent > 90:  # Alert at 90% memory usage
            alerts.append(f"High memory usage: {memory_percent:.1f}%")
        
        if queue_size > multi_camera_config.MAX_QUEUE_SIZE * 0.8:  # Alert at 80% queue capacity
            alerts.append(f"High queue usage: {queue_size}")
        
        if alerts:
            logger.logger.warning(f"Performance alerts: {', '.join(alerts)}")
    
    def increment_frames_processed(self, count=1):
        """Increment frames processed counter"""
        self.total_frames_processed += count
    
    def increment_detections(self, count=1):
        """Increment detections counter"""
        self.total_detections += count
    
    def increment_errors(self, camera_id=None, count=1):
        """Increment error counters"""
        self.detection_errors += count
        if camera_id:
            self.camera_errors[camera_id] += count
    
    def get_current_metrics(self):
        """Get current performance metrics"""
        current_time = datetime.now()
        elapsed_seconds = (current_time - self.start_time).total_seconds() if self.start_time else 0
        
        with self.lock:
            latest_metrics = {}
            for key, values in self.metrics_history.items():
                if values:
                    latest_metrics[key] = values[-1]
        
        return {
            'current_time': current_time,
            'uptime_seconds': elapsed_seconds,
            'counters': {
                'total_frames_processed': self.total_frames_processed,
                'total_detections': self.total_detections,
                'detection_errors': self.detection_errors,
                'camera_errors': dict(self.camera_errors)
            },
            'latest_metrics': latest_metrics,
            'rates': {
                'fps_average': self.total_frames_processed / max(elapsed_seconds, 1),
                'detections_per_hour': self.total_detections / max(elapsed_seconds, 1) * 3600,
                'errors_per_hour': self.detection_errors / max(elapsed_seconds, 1) * 3600
            }
        }
    
    def get_metrics_history(self, minutes=60):
        """Get metrics history for the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            filtered_metrics = defaultdict(list)
            
            for i, timestamp in enumerate(self.metrics_history['timestamp']):
                if timestamp >= cutoff_time:
                    for key, values in self.metrics_history.items():
                        if i < len(values):
                            filtered_metrics[key].append(values[i])
        
        return dict(filtered_metrics)
    
    def reset_counters(self):
        """Reset performance counters"""
        self.total_frames_processed = 0
        self.total_detections = 0
        self.detection_errors = 0
        self.camera_errors.clear()
        self.last_reset_time = datetime.now()
        
        logger.logger.info("Performance counters reset")
    
    def get_camera_statistics(self):
        """Get per-camera statistics"""
        if not self.service or not hasattr(self.service, 'active_cameras'):
            return {}
        
        stats = {}
        with self.service.lock:
            for camera_id, info in self.service.active_cameras.items():
                camera = info.get('camera')
                stats[camera_id] = {
                    'name': camera.name if camera else 'Unknown',
                    'location': camera.location if camera else 'Unknown',
                    'frame_count': info.get('frame_count', 0),
                    'last_detection': info.get('last_detection'),
                    'error_count': self.camera_errors.get(camera_id, 0),
                    'active': info.get('active', False),
                    'queue_size': self.service.detection_queues.get(camera_id, type('obj', (object,), {'qsize': lambda: 0})).qsize()
                }
        
        return stats
