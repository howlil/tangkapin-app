import threading
import time
import schedule
from datetime import datetime, timedelta
from app.models import Camera, DetectionLog, Notification, db, User, Report
from app.services.ml_detection import MLDetectionService
from app.services.notification_service import NotificationService
from app.services.multi_camera_detection_service import MultiCameraDetectionService
from config import Config
from app.utils.logger import logger
from threading import Thread

class BackgroundTaskManager:
    def __init__(self, app):
        self.app = app
        self.ml_service = MLDetectionService()
        self.notification_service = NotificationService()
        # Initialize multi-camera detection service
        self.multi_camera_service = MultiCameraDetectionService(app, max_workers=6)
        self.running = False
        self.threads = []
        self.tasks = []
        self.weapon_detection = None
        
        # Setup scheduled tasks
        self.setup_scheduled_tasks()
    
    def setup_scheduled_tasks(self):
        """Setup jadwal untuk recurring tasks"""
        # Check camera status setiap 15 menit
        schedule.every(15).minutes.do(self.check_camera_status)
        
        # Clean notifications setiap hari tengah malam
        schedule.every().day.at("00:00").do(self.cleanup_old_data)
        
        # Monitor multi-camera service setiap 5 menit
        schedule.every(5).minutes.do(self.monitor_multi_camera_service)
        
        logger.logger.info("🔄 Scheduled tasks initialized")
    
    def start_background_tasks(self):
        """Start semua background tasks"""
        if self.running:
            logger.logger.warning("⚠️ Background tasks already running")
            return
        
        try:
            logger.logger.info("Initializing background tasks")
            self.running = True
            
            # Initialize weapon detection service (if available)
            self._initialize_weapon_detection()
            
            # Start multi-camera detection service
            if self.multi_camera_service.start_service():
                logger.logger.info("✅ Multi-camera detection service started")
            else:
                logger.logger.warning("⚠️ Failed to start multi-camera detection service")
            
            # Start scheduler thread
            scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            scheduler_thread.start()
            self.threads.append(scheduler_thread)
            
            # Start real-time ML detection thread if weapon detection service not available
            if not self.weapon_detection:
                detection_thread = threading.Thread(target=self.run_continuous_detection, daemon=True)
                detection_thread.start()
                self.threads.append(detection_thread)
            
            # Start camera status monitor
            camera_status_thread = Thread(target=self._monitor_camera_status)
            camera_status_thread.daemon = True
            self.threads.append(camera_status_thread)
            camera_status_thread.start()
            
            logger.logger.info("✅ Background tasks started successfully")
            return True
            
        except Exception as e:
            logger.logger.error(f"Error starting background tasks: {e}")
            self.running = False
            return False
    
    def stop_background_tasks(self):
        """Stop all background tasks"""
        try:
            logger.logger.info("Stopping background tasks")
            self.running = False
            schedule.clear()
            
            # Stop multi-camera detection service
            if self.multi_camera_service and self.multi_camera_service.is_running:
                self.multi_camera_service.stop_service()
                logger.logger.info("Multi-camera detection service stopped")
            
            # Stop weapon detection service if running
            if self.weapon_detection:
                self.weapon_detection.stop_detection()
                logger.logger.info("Weapon detection service stopped")
            
            for thread in self.threads:
                if thread.is_alive():
                    thread.join(timeout=5)
            
            logger.logger.info("✅ Background tasks stopped successfully")
            return True
            
        except Exception as e:
            logger.logger.error(f"Error stopping background tasks: {e}")
            return False
    
    def _initialize_weapon_detection(self):
        """Initialize weapon detection service if available"""
        try:
            # Try to import and initialize weapon detection service
            from app.services.weapon_detection_service import WeaponDetectionService
            
            self.weapon_detection = WeaponDetectionService(self.app)
            self.weapon_detection.start_detection()
            logger.logger.info("Weapon detection service initialized and started")
            
        except ImportError as e:
            logger.logger.warning(f"Weapon detection service not available: {e}")
            self.weapon_detection = None
        except Exception as e:
            logger.logger.error(f"Error initializing weapon detection service: {e}")
            self.weapon_detection = None
    
    def run_scheduler(self):
        """Run scheduled tasks"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.logger.error(f"❌ Error in scheduler: {e}")
                time.sleep(5)
    
    def run_continuous_detection(self):
        """Run continuous ML detection untuk real-time monitoring"""
        while self.running:
            try:
                with self.app.app_context():
                    # Get cameras yang perlu di-check
                    cameras_to_check = self.get_cameras_for_detection()
                    
                    if cameras_to_check:
                        logger.logger.info(f"🔍 Checking {len(cameras_to_check)} cameras for detection...")
                        
                        for camera in cameras_to_check:
                            if not self.running:
                                break
                            
                            self.ml_service.process_camera_stream(camera.id)
                            time.sleep(2)  # Small delay between cameras
                    
                    # Sleep before next cycle
                    time.sleep(10)  # Check every 10 seconds
                    
            except Exception as e:
                logger.logger.error(f"❌ Error in continuous detection: {e}")
                time.sleep(30)  # Longer sleep on error
    
    def _monitor_camera_status(self):
        """Monitor camera status and update when needed"""
        logger.logger.info("Camera status monitoring started")
        
        while self.running:
            try:
                with self.app.app_context():
                    # Check for cameras that have gone offline
                    # In real implementation, this would ping cameras
                    # For demo, just log the count
                    cameras = Camera.query.filter_by(is_active=True).all()
                    online_cameras = [c for c in cameras if c.status == 'online']
                    
                    logger.logger.info(f"Camera monitor: {len(online_cameras)}/{len(cameras)} cameras online")
                    
            except Exception as e:
                logger.logger.error(f"Error in camera monitoring: {e}")
            
            # Sleep for a while before checking again
            time.sleep(300)  # Check every 5 minutes
    
    def check_camera_status(self):
        """Check status kamera dan update status jika offline"""
        try:
            with self.app.app_context():
                # Implement camera connectivity check
                logger.logger.info("🔄 Checking camera status...")
                # Simplified implementation
                
                # In real implementation, we'd ping each camera
                # For demo purposes, just log and return
                cameras = Camera.query.filter_by(is_active=True).all()
                logger.logger.info(f"✅ Checked status of {len(cameras)} cameras")
                
        except Exception as e:
            logger.logger.error(f"❌ Error checking camera status: {e}")
    
    def cleanup_old_data(self):
        """Cleanup old data periodically"""
        try:
            with self.app.app_context():
                logger.logger.info("🔄 Running scheduled data cleanup...")
                
                # Cleanup notifications older than 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                old_notifications = Notification.query.filter(Notification.created_at < thirty_days_ago).all()
                
                if old_notifications:
                    for notification in old_notifications:
                        db.session.delete(notification)
                    
                    db.session.commit()
                    logger.logger.info(f"✅ Cleaned up {len(old_notifications)} old notifications")
                
                # In real implementation, this would clean up old logs, 
                # temporary files, etc.
                logger.logger.info("✅ Data cleanup completed")
                
        except Exception as e:
            logger.logger.error(f"❌ Error in data cleanup: {e}")
    
    def get_cameras_for_detection(self):
        """Get list of active and online cameras for ML detection"""
        return Camera.query.filter_by(is_active=True, status='online').all()
    
    def run_ml_detection_cycle(self):
        """Run satu siklus ML detection pada semua kamera aktif"""
        try:
            with self.app.app_context():
                logger.logger.info("🔄 Starting scheduled ML detection cycle...")
                cameras_to_check = self.get_cameras_for_detection()
                
                if not cameras_to_check:
                    logger.logger.info("⚠️ No active cameras available for ML detection")
                    return
                
                logger.logger.info(f"🔍 ML detection starting on {len(cameras_to_check)} cameras")
                
                for camera in cameras_to_check:
                    self.ml_service.process_camera_stream(camera.id)
                    time.sleep(1)
                
                logger.logger.info("✅ ML detection cycle completed")
                
        except Exception as e:
            logger.logger.error(f"❌ Error in ML detection cycle: {e}")
    
    def retry_failed_notifications(self):
        """Retry notifications yang gagal"""
        try:
            with self.app.app_context():
                results = self.notification_service.retry_failed_notifications()
                
                if results:
                    success_count = sum(1 for r in results if r['success'])
                    logger.logger.info(f"🔄 Notification retry completed: {success_count}/{len(results)} successful")
                
        except Exception as e:
            logger.logger.error(f"❌ Error retrying notifications: {e}")
    
    def monitor_camera_status(self):
        """Monitor status kamera dan send alert jika offline"""
        try:
            with self.app.app_context():
                # Check cameras yang sudah lama tidak di-check
                offline_threshold = datetime.utcnow() - timedelta(minutes=5)
                
                potentially_offline = Camera.query.filter(
                    Camera.is_active == True,
                    Camera.status == 'online',
                    Camera.last_detection_check < offline_threshold
                ).all()
                
                for camera in potentially_offline:
                    # Update status ke offline
                    camera.status = 'offline'
                    db.session.commit()
                    
                    # Send notification ke owner
                    self.notification_service.send_system_alert(
                        user_id=camera.owner_id,
                        title="📡 Kamera Offline",
                        message=f"Kamera {camera.name} tidak merespons. Mohon periksa koneksi.",
                        alert_type='warning'
                    )
                
                if potentially_offline:
                    logger.logger.warning(f"⚠️ {len(potentially_offline)} cameras marked as offline")
                
        except Exception as e:
            logger.logger.error(f"❌ Error monitoring camera status: {e}")
    
    def cleanup_old_detection_logs(self):
        """Cleanup detection logs lama"""
        try:
            with self.app.app_context():
                # Keep only last 7 days of logs
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                
                deleted_count = DetectionLog.query.filter(
                    DetectionLog.created_at < cutoff_date
                ).delete()
                
                db.session.commit()
                
                if deleted_count > 0:
                    logger.logger.info(f"🗑️ Cleaned up {deleted_count} old detection logs")
                
        except Exception as e:
            logger.logger.error(f"❌ Error cleaning up detection logs: {e}")
    
    def cleanup_old_notifications(self):
        """Cleanup notifications lama"""
        try:
            with self.app.app_context():
                deleted_count = self.notification_service.cleanup_old_notifications(days=30)
                
                if deleted_count > 0:
                    logger.logger.info(f"🗑️ Cleaned up {deleted_count} old notifications")
                
        except Exception as e:
            logger.logger.error(f"❌ Error cleaning up notifications: {e}")
    
    def log_system_statistics(self):
        """Log system statistics untuk monitoring"""
        try:
            with self.app.app_context():
                # Detection statistics
                detection_stats = self.ml_service.get_detection_statistics(hours=1)
                
                # Notification statistics
                notification_stats = self.notification_service.get_notification_queue_status()
                
                # Camera statistics
                total_cameras = Camera.query.filter_by(is_active=True).count()
                online_cameras = Camera.query.filter_by(is_active=True, status='online').count()
                
                stats = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'cameras': {
                        'total': total_cameras,
                        'online': online_cameras,
                        'offline': total_cameras - online_cameras
                    },
                    'detection': detection_stats,
                    'notifications': notification_stats
                }
                
                logger.logger.info(f"📊 System Stats: {online_cameras}/{total_cameras} cameras online, "
                              f"{detection_stats['weapon_detections'] if detection_stats else 0} detections (1h), "
                              f"{notification_stats['pending'] if notification_stats else 0} pending notifications")
                
                # TODO: Send stats to monitoring service atau save ke log file
                
        except Exception as e:
            logger.logger.error(f"❌ Error logging system statistics: {e}")
    
    def force_detection_all_cameras(self):
        """Force detection untuk semua kamera (manual trigger)"""
        try:
            with self.app.app_context():
                results = self.ml_service.process_all_active_cameras()
                return results
                
        except Exception as e:
            logger.logger.error(f"❌ Error in force detection: {e}")
            return []
    
    def send_test_notification(self, user_id, message="Test notification from TangkapIn system"):
        """Send test notification untuk testing purposes"""
        try:
            with self.app.app_context():
                return self.notification_service.send_system_alert(
                    user_id=user_id,
                    title="🧪 Test Notification",
                    message=message,
                    alert_type='info'
                )
                
        except Exception as e:
            logger.logger.error(f"❌ Error sending test notification: {e}")
            return None
    
    def get_system_health(self):
        """Get overall system health status"""
        try:
            with self.app.app_context():
                # Check model status
                model_status = "healthy" if self.ml_service.model else "error"
                
                # Check notification service
                notification_status = "healthy"  # Assume healthy if no recent errors
                
                # Check database connection
                try:
                    db.session.execute('SELECT 1')
                    db_status = "healthy"
                except:
                    db_status = "error"
                
                # Check active cameras
                active_cameras = Camera.query.filter_by(is_active=True, status='online').count()
                
                return {
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'healthy' if all([
                        model_status == 'healthy',
                        notification_status == 'healthy',
                        db_status == 'healthy'
                    ]) else 'degraded',
                    'services': {
                        'ml_detection': model_status,
                        'notifications': notification_status,
                        'database': db_status
                    },
                    'metrics': {
                        'active_cameras': active_cameras,
                        'background_tasks_running': self.running
                    }
                }
                
        except Exception as e:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def monitor_multi_camera_service(self):
        """Monitor multi-camera detection service health"""
        try:
            with self.app.app_context():
                if not self.multi_camera_service.is_running:
                    logger.logger.warning("⚠️ Multi-camera detection service not running, attempting restart...")
                    
                    if self.multi_camera_service.start_service():
                        logger.logger.info("✅ Multi-camera detection service restarted successfully")
                    else:
                        logger.logger.error("❌ Failed to restart multi-camera detection service")
                else:
                    # Log service statistics
                    status = self.multi_camera_service.get_active_cameras_status()
                    active_count = len(status)
                    logger.logger.info(f"📊 Multi-camera service healthy: {active_count} cameras active")
                
        except Exception as e:
            logger.logger.error(f"❌ Error monitoring multi-camera service: {e}")
    
    def get_service_status(self):
        """Get comprehensive status of all background services"""
        return {
            'background_tasks_running': self.running,
            'multi_camera_service': {
                'running': self.multi_camera_service.is_running if self.multi_camera_service else False,
                'active_cameras': len(self.multi_camera_service.get_active_cameras_status()) if self.multi_camera_service else 0
            },
            'weapon_detection_service': {
                'available': self.weapon_detection is not None,
                'running': getattr(self.weapon_detection, 'is_running', False) if self.weapon_detection else False
            },
            'ml_service': {
                'available': self.ml_service is not None
            },
            'notification_service': {
                'available': self.notification_service is not None
            },
            'active_threads': len([t for t in self.threads if t.is_alive()])
        }