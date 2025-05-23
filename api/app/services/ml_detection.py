import cv2
import torch
import numpy as np
import time
import os
from datetime import datetime
from PIL import Image
import uuid
from config import Config
from app.models import Camera, DetectionLog, Report, User, db
from app.services.notification_service import NotificationService

class MLDetectionService:
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.confidence_threshold = Config.DETECTION_CONFIDENCE_THRESHOLD
        self.model_version = "1.0.0"
        self.notification_service = NotificationService()
        self.load_model()
    
    def load_model(self):
        """Load PyTorch model untuk weapon detection"""
        try:
            if os.path.exists(Config.ML_MODEL_PATH):
                self.model = torch.load(Config.ML_MODEL_PATH, map_location=self.device)
                self.model.eval()
                print(f"✅ ML Model loaded successfully from {Config.ML_MODEL_PATH}")
            else:
                print(f"❌ ML Model not found at {Config.ML_MODEL_PATH}")
                # Create dummy model untuk testing
                self.create_dummy_model()
        except Exception as e:
            print(f"❌ Error loading ML model: {e}")
            self.create_dummy_model()
    
    def create_dummy_model(self):
        """Create dummy model untuk testing (jika model asli belum ada)"""
        print("🔧 Creating dummy model for testing...")
        self.model = "dummy_model"  # Placeholder
    
    def process_camera_stream(self, camera_id):
        """Process CCTV stream untuk deteksi senjata"""
        start_time = time.time()
        
        try:
            camera = Camera.query.get(camera_id)
            if not camera or not camera.is_active or camera.status != 'online':
                return None
            
            # Log detection attempt
            detection_log = DetectionLog(
                camera_id=camera_id,
                status='processing',
                model_version=self.model_version
            )
            db.session.add(detection_log)
            db.session.commit()
            
            # Process stream
            detection_result = self._detect_weapons_in_stream(camera.stream_url)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update detection log
            detection_log.processing_time = processing_time
            detection_log.status = 'detected' if detection_result['weapon_detected'] else 'no_detection'
            detection_log.confidence_score = detection_result.get('confidence', 0)
            detection_log.weapon_detected = detection_result.get('weapon_type')
            detection_log.detection_image_path = detection_result.get('image_path')
            detection_log.raw_output = detection_result
            
            # Update camera last check
            camera.last_detection_check = datetime.utcnow()
            
            db.session.commit()
            
            # Jika weapon terdeteksi, create auto report
            if detection_result['weapon_detected'] and detection_result['confidence'] >= self.confidence_threshold:
                self._create_auto_report(camera, detection_log, detection_result)
            
            return detection_result
            
        except Exception as e:
            # Log error
            if 'detection_log' in locals():
                detection_log.status = 'error'
                detection_log.error_message = str(e)
                detection_log.processing_time = time.time() - start_time
                db.session.commit()
            
            print(f"❌ Error processing camera {camera_id}: {e}")
            return None
    
    def _detect_weapons_in_stream(self, stream_url):
        """Detect weapons menggunakan ML model"""
        try:
            # Capture frame dari CCTV stream
            cap = cv2.VideoCapture(stream_url)
            
            if not cap.isOpened():
                # Untuk testing, return dummy result
                return self._get_dummy_detection_result()
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return {'weapon_detected': False, 'confidence': 0}
            
            # Detect weapons in the captured frame
            result = self._detect_weapons_in_frame(frame)
            
            return result
            
        except Exception as e:
            print(f"❌ Error in weapon detection: {e}")
            return {'weapon_detected': False, 'confidence': 0, 'error': str(e)}
    
    def _detect_weapons_in_frame(self, frame):
        """Detect weapons in a single frame"""
        try:
            # Jika model dummy (untuk testing)
            if self.model == "dummy_model":
                return self._get_dummy_detection_result()
            
            # Process frame dengan real model
            result = self._run_model_inference(frame)
            
            # Save detection image jika weapon terdeteksi
            if result['weapon_detected']:
                image_path = self._save_detection_image(frame)
                result['image_path'] = image_path
            
            return result
            
        except Exception as e:
            print(f"❌ Error in weapon detection: {e}")
            return {'weapon_detected': False, 'confidence': 0, 'error': str(e)}
    
    def _get_dummy_detection_result(self):
        """Generate dummy detection result untuk testing"""
        import random
        
        # 20% chance weapon detected untuk testing
        weapon_detected = random.random() < 0.2
        
        if weapon_detected:
            weapon_types = ['knife', 'gun', 'machete']
            return {
                'weapon_detected': True,
                'confidence': round(random.uniform(0.7, 0.95), 2),
                'weapon_type': random.choice(weapon_types),
                'bbox': [100, 100, 200, 200],  # dummy bounding box
                'image_path': None
            }
        else:
            return {
                'weapon_detected': False,
                'confidence': round(random.uniform(0.1, 0.4), 2)
            }
    
    def _run_model_inference(self, frame):
        """Run inference menggunakan real PyTorch model"""
        try:
            # Preprocess frame
            input_tensor = self._preprocess_frame(frame)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(input_tensor)
            
            # Process outputs
            result = self._process_model_output(outputs)
            
            return result
            
        except Exception as e:
            print(f"❌ Error in model inference: {e}")
            return {'weapon_detected': False, 'confidence': 0, 'error': str(e)}
    
    def _preprocess_frame(self, frame):
        """Preprocess frame untuk model input"""
        # Resize frame ke input size model (contoh: 640x640)
        resized = cv2.resize(frame, (640, 640))
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize
        normalized = rgb.astype(np.float32) / 255.0
        
        # Convert to tensor
        tensor = torch.from_numpy(normalized).permute(2, 0, 1).unsqueeze(0)
        
        return tensor.to(self.device)
    
    def _process_model_output(self, outputs):
        """Process output dari YOLO model"""
        # Contoh processing untuk YOLO output
        # Sesuaikan dengan format output model Anda
        
        detections = outputs[0]  # Asumsi batch size 1
        
        # Filter detections dengan confidence > threshold
        confident_detections = detections[detections[:, 4] > self.confidence_threshold]
        
        if len(confident_detections) > 0:
            # Ambil detection dengan confidence tertinggi
            best_detection = confident_detections[confident_detections[:, 4].argmax()]
            
            # Map class ID ke nama weapon (sesuaikan dengan model Anda)
            weapon_classes = {0: 'knife', 1: 'gun', 2: 'machete'}
            class_id = int(best_detection[5])
            weapon_type = weapon_classes.get(class_id, 'unknown')
            
            return {
                'weapon_detected': True,
                'confidence': float(best_detection[4]),
                'weapon_type': weapon_type,
                'bbox': best_detection[:4].tolist()
            }
        else:
            return {'weapon_detected': False, 'confidence': 0}
    
    def _save_detection_image(self, frame):
        """Save image saat weapon terdeteksi"""
        try:
            # Create detection images directory jika belum ada
            detection_dir = Config.DETECTION_IMAGE_PATH
            os.makedirs(detection_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{timestamp}_{str(uuid.uuid4())[:8]}.jpg"
            filepath = os.path.join(detection_dir, filename)
            
            # Save image
            cv2.imwrite(filepath, frame)
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving detection image: {e}")
            return None
    
    def _create_auto_report(self, camera, detection_log, detection_result):
        """Create automatic report dari weapon detection"""
        try:
            # Create auto report
            report = Report(
                title=f"🚨 Deteksi Senjata - {camera.name}",
                description=f"Sistem mendeteksi {detection_result['weapon_type']} dengan confidence {detection_result['confidence']*100:.1f}%",
                camera_id=camera.id,
                reporter_id=camera.owner_id,  # System menggunakan owner sebagai reporter
                status='NEW',
                priority='CRITICAL',  # Weapon detection = CRITICAL priority
                detection_confidence=detection_result['confidence'],
                weapon_type=detection_result['weapon_type'],
                detection_image_url=detection_result.get('image_path'),
                is_automatic=True,
                detection_log_id=detection_log.id
            )
            
            db.session.add(report)
            db.session.commit()
            
            print(f"✅ Auto report created: {report.id}")
            
            # Send notifications
            self._send_detection_notifications(camera, report, detection_result)
            
            return report
            
        except Exception as e:
            print(f"❌ Error creating auto report: {e}")
            db.session.rollback()
            return None
    
    def _send_detection_notifications(self, camera, report, detection_result):
        """Send notifications untuk weapon detection"""
        try:
            # Notifikasi ke owner
            self.notification_service.send_weapon_detection_alert(
                user_id=camera.owner_id,
                report_id=report.id,
                camera_name=camera.name,
                weapon_type=detection_result['weapon_type'],
                confidence=detection_result['confidence']
            )
            
            # Notifikasi ke semua admin
            admins = User.query.filter_by(role='admin', is_active=True).all()
            for admin in admins:
                self.notification_service.send_weapon_detection_alert(
                    user_id=admin.id,
                    report_id=report.id,
                    camera_name=camera.name,
                    weapon_type=detection_result['weapon_type'],
                    confidence=detection_result['confidence']
                )
            
        except Exception as e:
            print(f"❌ Error sending detection notifications: {e}")
    
    def process_all_active_cameras(self):
        """Process semua kamera aktif untuk detection"""
        try:
            active_cameras = Camera.query.filter_by(
                is_active=True, 
                status='online'
            ).all()
            
            results = []
            for camera in active_cameras:
                result = self.process_camera_stream(camera.id)
                if result:
                    results.append({
                        'camera_id': camera.id,
                        'camera_name': camera.name,
                        'result': result
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing all cameras: {e}")
            return []
    
    def get_detection_statistics(self, hours=24):
        """Get statistik detection dalam X jam terakhir"""
        try:
            from datetime import timedelta
            
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            total_checks = DetectionLog.query.filter(
                DetectionLog.created_at >= start_time
            ).count()
            
            weapon_detections = DetectionLog.query.filter(
                DetectionLog.created_at >= start_time,
                DetectionLog.status == 'detected'
            ).count()
            
            avg_processing_time = db.session.query(
                db.func.avg(DetectionLog.processing_time)
            ).filter(
                DetectionLog.created_at >= start_time,
                DetectionLog.processing_time.isnot(None)
            ).scalar() or 0
            
            return {
                'total_checks': total_checks,
                'weapon_detections': weapon_detections,
                'detection_rate': (weapon_detections / total_checks * 100) if total_checks > 0 else 0,
                'avg_processing_time': round(avg_processing_time, 2),
                'period_hours': hours
            }
            
        except Exception as e:
            print(f"❌ Error getting detection statistics: {e}")
            return None