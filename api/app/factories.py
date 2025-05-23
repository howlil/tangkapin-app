from faker import Faker
import random
from datetime import datetime, timedelta
import uuid
from app.models import (
    User, Camera, Report, Evidence, Assignment, Location, 
    TimelineEvent, Notification, ReportUpdate, PerformanceMetric, 
    TokenBlacklist, db, UserRole
)

# Initialize faker dengan locale Indonesia
fake = Faker('id_ID')

class UserFactory:
    @staticmethod
    def create_admin(email=None, name=None):
        """Create admin user"""
        user = User(
            email=email or fake.email(),
            name=name or fake.name(),
            phone=fake.phone_number()[:20],
            address=fake.address(),
            role=UserRole.ADMIN,  # Use enum instead of string
            badge_number=f"ADM{fake.random_int(min=1000, max=9999)}",
            longitude=str(fake.longitude()),  # Correct field name
            latitude=str(fake.latitude()),   # Correct field name
            fcm_token=fake.uuid4(),
            is_active=True,
            last_login=fake.date_time_between(start_date='-30d', end_date='now')
        )
        # Set password default
        user.set_password('password123')
        return user
    
    @staticmethod
    def create_officer(email=None, name=None):
        """Create officer user"""
        user = User(
            email=email or fake.email(),
            name=name or fake.name(),
            phone=fake.phone_number()[:20],
            address=fake.address(),
            role=UserRole.OFFICER,  # Use enum instead of string
            badge_number=f"POL{fake.random_int(min=10000, max=99999)}",
            longitude=str(fake.longitude()),  # Correct field name
            latitude=str(fake.latitude()),   # Correct field name
            fcm_token=fake.uuid4(),
            is_active=True,
            last_login=fake.date_time_between(start_date='-7d', end_date='now')
        )
        # Set password default
        user.set_password('password123')
        return user
    
    @staticmethod
    def create_owner(email=None, name=None):
        """Create minimarket owner"""
        user = User(
            email=email or fake.email(),
            name=name or fake.name(),
            phone=fake.phone_number()[:20],
            address=fake.address(),
            role=UserRole.OWNER,  # Use enum instead of string
            badge_number=None,
            longitude=str(fake.longitude()),  # Correct field name
            latitude=str(fake.latitude()),   # Correct field name
            fcm_token=fake.uuid4(),
            is_active=True,
            last_login=fake.date_time_between(start_date='-3d', end_date='now')
        )
        # Set password default
        user.set_password('password123')
        return user
    
    @staticmethod
    def create_bulk_users(admins=2, officers=10, owners=20):
        """Create multiple users at once"""
        users = []
        
        # Create admins
        for i in range(admins):
            users.append(UserFactory.create_admin())
        
        # Create officers
        for i in range(officers):
            users.append(UserFactory.create_officer())
        
        # Create owners
        for i in range(owners):
            users.append(UserFactory.create_owner())
        
        return users

class CameraFactory:
    @staticmethod
    def create(owner_id):
        """Create camera for owner"""
        from app.models import CameraStatus
        
        minimarket_names = [
            "Indomaret", "Alfamart", "Circle K", "Lawson", "FamilyMart",
            "Minimarket Berkah", "Toko Sari", "Warung Maju", "Mart 24",
            "Minimart Sejahtera"
        ]
        
        locations = [
            "Jakarta Pusat", "Jakarta Selatan", "Jakarta Utara", "Jakarta Barat", "Jakarta Timur",
            "Bandung", "Surabaya", "Medan", "Semarang", "Makassar", "Palembang", "Yogyakarta",
            "Padang", "Denpasar", "Balikpapan", "Malang", "Solo", "Bekasi", "Tangerang", "Depok"
        ]
        
        store_name = random.choice(minimarket_names)
        location = random.choice(locations)
        
        return Camera(
            name=f"CCTV {store_name} {location}",
            description=f"Kamera keamanan untuk monitoring {store_name} cabang {location}",
            location=f"{store_name} - Jl. {fake.street_name()} No.{fake.building_number()}, {location}",
            latitude=fake.latitude(),
            longitude=fake.longitude(),
            stream_url=f"rtsp://192.168.{fake.random_int(1, 254)}.{fake.random_int(1, 254)}:554/stream",
            cctv_ip=fake.ipv4_private(),
            status=random.choice([CameraStatus.ONLINE, CameraStatus.OFFLINE, CameraStatus.MAINTENANCE]),
            owner_id=owner_id,
            is_active=True,
            last_online=fake.date_time_between(start_date='-1d', end_date='now') if random.random() > 0.2 else None
        )
    
    @staticmethod
    def create_multiple(owner_id, count=3):
        """Create multiple cameras for an owner"""
        cameras = []
        for _ in range(count):
            cameras.append(CameraFactory.create(owner_id))
        return cameras

class ReportFactory:
    @staticmethod
    def create_manual(camera_id, reporter_id):
        """Create manual report"""
        from app.models import ReportStatus, ReportPriority
        
        incident_types = [
            "Penyusupan mencurigakan",
            "Aktivitas tidak normal", 
            "Gangguan keamanan",
            "Pencurian terdeteksi",
            "Perampokan bersenjata",
            "Kerusuhan di area toko"
        ]
        
        return Report(
            title=random.choice(incident_types),
            description=fake.text(max_nb_chars=200),
            camera_id=camera_id,
            reporter_id=reporter_id,
            status=random.choice([ReportStatus.NEW, ReportStatus.VERIFIED, ReportStatus.ASSIGNED, 
                                ReportStatus.IN_PROGRESS, ReportStatus.COMPLETED, ReportStatus.FALSE_ALARM]),
            priority=random.choice([ReportPriority.LOW, ReportPriority.MEDIUM, 
                                  ReportPriority.HIGH, ReportPriority.CRITICAL]),
            detection_confidence=None,
            weapon_type=None,
            detection_image_url=None,
            is_automatic=False,
            is_active=True
        )
    
    @staticmethod
    def create_automatic(camera_id, reporter_id):
        """Create automatic report from ML detection dengan Supabase URL"""
        from app.models import ReportStatus, ReportPriority
        
        weapon_types = ['knife', 'gun', 'machete', 'sword', 'pistol']
        weapon_type = random.choice(weapon_types)
        confidence = round(random.uniform(0.7, 0.98), 2)
        
        # Generate dummy Supabase URL untuk detection image
        supabase_base_url = "https://your-project.supabase.co/storage/v1/object/public"
        bucket = "detection-images"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"cameras/{camera_id}/detections/{timestamp}_{fake.uuid4()[:8]}.jpg"
        supabase_url = f"{supabase_base_url}/{bucket}/{filepath}"
        
        return Report(
            title=f"🚨 DETEKSI SENJATA - {weapon_type.upper()}",
            description=f"Sistem mendeteksi {weapon_type} dengan tingkat kepercayaan {confidence*100:.1f}%. Mohon segera verifikasi dan tindak lanjut.",
            camera_id=camera_id,
            reporter_id=reporter_id,
            status=ReportStatus.NEW,
            priority=ReportPriority.CRITICAL,
            detection_confidence=confidence,
            weapon_type=weapon_type,
            detection_image_url=supabase_url,
            is_automatic=True,
            is_active=True
        )

class NotificationFactory:
    @staticmethod
    def create_weapon_detection(user_id, reference_id):
        """Create weapon detection notification"""
        from app.models import NotificationType
        
        weapon_types = ['pisau', 'senjata api', 'parang', 'pedang']
        weapon = random.choice(weapon_types)
        
        return Notification(
            user_id=user_id,
            title="🚨 DETEKSI SENJATA!",
            message=f"Sistem mendeteksi {weapon} di lokasi Anda. Mohon segera periksa dan laporkan ke pihak berwajib.",
            notification_type=NotificationType.EMERGENCY,  # Use enum
            reference_id=reference_id,
            is_read=random.choice([True, False])
        )
    
    @staticmethod
    def create_assignment(user_id, reference_id):
        """Create assignment notification"""
        from app.models import NotificationType
        
        return Notification(
            user_id=user_id,
            title="📋 Penugasan Baru",
            message=f"Anda mendapat penugasan baru. Mohon segera cek dan konfirmasi penerimaan tugas.",
            notification_type=NotificationType.ASSIGNMENT,  # Use enum
            reference_id=reference_id,
            is_read=random.choice([True, False])
        )
    
    @staticmethod
    def create_system_alert(user_id):
        """Create system alert notification"""
        from app.models import NotificationType
        
        alerts = [
            "Sistem dalam maintenance terjadwal",
            "Update keamanan telah tersedia",
            "Kamera offline terdeteksi",
            "Laporan bulanan telah dibuat"
        ]
        
        return Notification(
            user_id=user_id,
            title="🔔 Notifikasi Sistem",
            message=random.choice(alerts),
            notification_type=NotificationType.SYSTEM,  # Use enum
            reference_id=None,
            is_read=random.choice([True, False])
        )
    
    @staticmethod
    def create_report_notification(user_id, reference_id):
        """Create report notification"""
        from app.models import NotificationType
        
        messages = [
            "Laporan baru telah dibuat dan memerlukan verifikasi",
            "Status laporan telah diperbarui",
            "Laporan Anda telah diverifikasi oleh admin",
            "Investigasi laporan telah selesai"
        ]
        
        return Notification(
            user_id=user_id,
            title="📄 Update Laporan",
            message=random.choice(messages),
            notification_type=NotificationType.REPORT,  # Use enum
            reference_id=reference_id,
            is_read=random.choice([True, False])
        )

# Helper function to seed specific admin user
def create_default_admin():
    """Create the default admin user that was failing in the seed"""
    admin = User(
        id='b2ee0d7a-6b94-4afc-ab00-f89f8dfe5447',  # Keep the same ID from error
        email='admin@tangkapin.com',
        name='Administrator',
        phone='(017) 119-3336',
        address='Jalan Setiabudhi No. 35\nTangerang, NT 60273',
        role=UserRole.ADMIN,
        badge_number='ADM8002',
        longitude='150.365438',
        latitude='51.7389625',
        fcm_token='b8b38ce5-23f1-4eaf-8963-b09fa5dca940',
        is_active=True,
        last_login=datetime(2025, 4, 24, 1, 46, 56),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    admin.set_password('password123')
    return admin