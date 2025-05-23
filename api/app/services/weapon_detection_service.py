import cv2
import numpy as np
import os
import time
import uuid
from datetime import datetime
from threading import Thread, Lock
from app.models import Report, Camera, Notification, db
from app.utils.logger import logger
from app.services.notification_service import NotificationService
from app.services.supabase_storage import SupabaseStorageService

class WeaponDetectionService:
    """Service for weapon detection from camera feeds"""
    
    def __init__(self, app=None):
        self.app = app
        self.active_cameras = {}  # {camera_id: camera_thread}
        self.lock = Lock()
        self.storage_service = SupabaseStorageService()
        self.notification_service = NotificationService()
        self.detection_model = None
        self.is_running = False
        self._load_weapon_detection_model()
    
    def _load_weapon_detection_model(self):
        """Load weapon detection model"""
        try:
            # Dalam implementasi nyata, ini akan memuat model ML seperti YOLOv8, Faster R-CNN, dll
            # Untuk contoh kode, kita simulasikan bahwa model berhasil dimuat
            logger.logger.info("Initializing weapon detection model")
            self.detection_model = {
                "name": "YOLOv8-weapon-detection",
                "version": "1.0",
                "classes": ["knife", "gun", "sword", "machete", "pistol"]
            }
            logger.logger.info("Weapon detection model loaded successfully")
        except Exception as e:
            logger.logger.error(f"Error loading weapon detection model: {e}")
    
    def start_detection(self):
        """Start weapon detection service"""
        if self.is_running:
            logger.logger.warning("Weapon detection service is already running")
            return False
        
        self.is_running = True
        Thread(target=self._monitor_cameras).start()
        logger.logger.info("Weapon detection service started")
        return True
    
    def stop_detection(self):
        """Stop weapon detection service"""
        self.is_running = False
        
        with self.lock:
            for camera_id, thread_info in self.active_cameras.items():
                thread_info["active"] = False
                logger.logger.info(f"Stopping detection for camera {camera_id}")
        
        logger.logger.info("Weapon detection service stopped")
        return True
    
    def _monitor_cameras(self):
        """Monitor all cameras and start detection threads"""
        while self.is_running:
            try:
                with self.app.app_context():
                    # Ambil semua kamera aktif dan online
                    cameras = Camera.query.filter_by(
                        is_active=True, 
                        status='online'
                    ).all()
                    
                    # Start detection untuk kamera baru
                    for camera in cameras:
                        with self.lock:
                            if camera.id not in self.active_cameras:
                                thread = Thread(
                                    target=self._process_camera_feed,
                                    args=(camera.id, camera.stream_url)
                                )
                                self.active_cameras[camera.id] = {
                                    "thread": thread,
                                    "active": True,
                                    "last_detection": None
                                }
                                thread.daemon = True
                                thread.start()
                                logger.logger.info(f"Started detection for camera {camera.id}: {camera.name}")
                            
                    # Hentikan detection untuk kamera yang tidak aktif
                    with self.lock:
                        camera_ids = [c.id for c in cameras]
                        for camera_id in list(self.active_cameras.keys()):
                            if camera_id not in camera_ids:
                                self.active_cameras[camera_id]["active"] = False
                                logger.logger.info(f"Marked camera {camera_id} for removal")
                
                    # Clean up kamera yang tidak aktif
                    with self.lock:
                        for camera_id in list(self.active_cameras.keys()):
                            if not self.active_cameras[camera_id]["active"]:
                                del self.active_cameras[camera_id]
                                logger.logger.info(f"Removed camera {camera_id} from active cameras")
            
            except Exception as e:
                logger.logger.error(f"Error in camera monitoring: {e}")
            
            # Sleep for a while before checking again
            time.sleep(60)  # Check setiap 1 menit
    
    def _process_camera_feed(self, camera_id, stream_url):
        """Process video feed from a camera"""
        logger.logger.info(f"Starting processing for camera {camera_id}")
        
        with self.app.app_context():
            try:
                camera = Camera.query.get(camera_id)
                if not camera:
                    logger.logger.error(f"Camera {camera_id} not found")
                    return
                
                # Dalam implementasi nyata, ini akan terhubung ke stream kamera sebenarnya
                # Untuk contoh kode, simulasikan proses deteksi
                
                # Simulasi frekuensi deteksi untuk contoh
                detection_interval = 5  # detik antara simulasi deteksi
                
                while self.active_cameras.get(camera_id, {}).get("active", False):
                    # Simulasi pembacaan frame
                    # frame = capture.read()
                    
                    # Simulasi deteksi senjata
                    if self._simulate_detection():
                        weapon_type = np.random.choice(self.detection_model["classes"])
                        confidence = np.random.uniform(0.70, 0.98)
                        
                        # Simpan gambar deteksi (disimulasikan)
                        image_path = self._save_detection_image(camera_id, weapon_type)
                        
                        # Buat laporan otomatis
                        self._create_automatic_report(camera_id, weapon_type, confidence, image_path)
                        
                        # Update waktu deteksi terakhir
                        with self.lock:
                            if camera_id in self.active_cameras:
                                self.active_cameras[camera_id]["last_detection"] = datetime.now()
                    
                    # Simulasi interval pemrosesan
                    time.sleep(detection_interval)
                
                logger.logger.info(f"Stopped processing for camera {camera_id}")
                
            except Exception as e:
                logger.logger.error(f"Error processing camera {camera_id}: {e}")
    
    def _simulate_detection(self):
        """Simulate random weapon detection for demonstration"""
        # Simulasi deteksi (sangat jarang terjadi untuk demo)
        return np.random.random() < 0.01  # 1% kemungkinan deteksi untuk simulasi
    
    def _save_detection_image(self, camera_id, weapon_type):
        """Save detection image to storage"""
        try:
            # Dalam implementasi nyata, ini akan menyimpan frame aktual
            # Untuk contoh kode, simulasikan penyimpanan gambar
            
            image_name = f"detection_{uuid.uuid4()}.jpg"
            image_path = f"/detection_images/{image_name}"
            
            logger.logger.info(f"Detection image saved: {image_path}")
            return image_path
            
        except Exception as e:
            logger.logger.error(f"Error saving detection image: {e}")
            return None
    
    def _create_automatic_report(self, camera_id, weapon_type, confidence, image_path):
        """Create automatic report from weapon detection"""
        try:
            with self.app.app_context():
                # Dapatkan informasi kamera
                camera = Camera.query.get(camera_id)
                if not camera:
                    logger.logger.error(f"Camera {camera_id} not found")
                    return
                
                # Admin user akan menjadi reporter (biasanya ID=1)
                admin_id = 1  # Ganti dengan admin ID yang sesuai
                
                # Buat laporan otomatis
                report = Report(
                    title=f"🚨 DETEKSI SENJATA - {weapon_type.upper()}",
                    description=f"Sistem mendeteksi {weapon_type} dengan tingkat kepercayaan {confidence*100:.1f}%. Mohon segera verifikasi dan tindak lanjut.",
                    camera_id=camera_id,
                    reporter_id=admin_id,
                    status='NEW',
                    priority='CRITICAL',
                    detection_confidence=confidence,
                    weapon_type=weapon_type,
                    detection_image_url=image_path,
                    is_automatic=True,
                    is_active=True
                )
                
                db.session.add(report)
                db.session.commit()
                
                logger.logger.info(f"Automatic report created for camera {camera_id}: {report.id}")
                
                # Kirim notifikasi ke owner kamera dan admin
                self._send_notifications(report, camera)
                
                return report
                
        except Exception as e:
            logger.logger.error(f"Error creating automatic report: {e}")
            return None
    
    def _send_notifications(self, report, camera):
        """Send notifications for weapon detection"""
        try:
            # Kirim notifikasi ke pemilik kamera
            self.notification_service.send_weapon_detection_alert(
                camera_id=camera.id,
                report_id=report.id,
                weapon_type=report.weapon_type
            )
            
            # Kirim notifikasi ke semua admin
            self.notification_service.send_admin_alert(
                report_id=report.id,
                camera_id=camera.id,
                alert_type="weapon_detection",
                message=f"DETEKSI SENJATA di {camera.name}.\nSilahkan verifikasi dan tindaklanjuti."
            )
            
            logger.logger.info(f"Notifications sent for report {report.id}")
            
        except Exception as e:
            logger.logger.error(f"Error sending notifications: {e}") 