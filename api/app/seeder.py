from faker import Faker
import random
from datetime import datetime, timedelta
import uuid
from app.models import (
    User, Camera, Report, Evidence, Assignment, Location, 
    TimelineEvent, Notification, ReportUpdate, PerformanceMetric, 
    TokenBlacklist, db
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
            role='admin',
            badge_number=f"ADM{fake.random_int(min=1000, max=9999)}",
            longitude=str(fake.longitude()),  # Fixed: was 'lang'
            latitude=str(fake.latitude()),    # Fixed: was 'lat'
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
            role='officer',
            badge_number=f"POL{fake.random_int(min=10000, max=99999)}",
            longitude=str(fake.longitude()),  # Fixed: was 'lang'
            latitude=str(fake.latitude()),    # Fixed: was 'lat'
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
            role='owner',
            badge_number=None,
            longitude=str(fake.longitude()),  # Fixed: was 'lang'
            latitude=str(fake.latitude()),    # Fixed: was 'lat'
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
            status=random.choice(['online', 'offline', 'maintenance']),
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
            status=random.choice(['NEW', 'VERIFIED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FALSE_ALARM']),
            priority=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
            detection_confidence=None,
            weapon_type=None,
            detection_image_url=None,
            is_automatic=False,
            is_active=True
        )
    
    @staticmethod
    def create_automatic(camera_id, reporter_id):  # Fixed: removed detection_log_id parameter
        """Create automatic report from ML detection dengan Supabase URL"""
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
            status='NEW',
            priority='CRITICAL',
            detection_confidence=confidence,
            weapon_type=weapon_type,
            detection_image_url=supabase_url,
            is_automatic=True,
            is_active=True
        )

class EvidenceFactory:
    @staticmethod
    def create(report_id, created_by):
        """Create evidence untuk report dengan Supabase Storage URL"""
        evidence_types = ['image', 'video', 'audio', 'document']
        file_type = random.choice(evidence_types)
        
        file_extensions = {
            'image': ['jpg', 'png', 'jpeg'],
            'video': ['mp4', 'avi', 'mov'],
            'audio': ['mp3', 'wav', 'm4a'],
            'document': ['pdf', 'doc', 'txt']
        }
        
        ext = random.choice(file_extensions[file_type])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evidence_{timestamp}_{fake.uuid4()[:8]}.{ext}"
        
        # Generate Supabase Storage URL
        supabase_base_url = "https://your-project.supabase.co/storage/v1/object/public"
        bucket = "evidence-files"
        filepath = f"reports/{report_id}/{file_type}/{filename}"
        supabase_url = f"{supabase_base_url}/{bucket}/{filepath}"
        
        return Evidence(
            report_id=report_id,
            file_url=supabase_url,
            file_type=file_type,
            description=f"Bukti {file_type} dari laporan - {fake.sentence()}",
            created_by=created_by
        )
    
    @staticmethod
    def create_multiple(report_id, created_by, count=3):
        """Create multiple evidences for a report"""
        evidences = []
        for _ in range(count):
            evidences.append(EvidenceFactory.create(report_id, created_by))
        return evidences

class AssignmentFactory:
    @staticmethod
    def create(report_id, officer_id, assigned_by):
        """Create assignment for officer"""
        status = random.choice(['PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'REJECTED'])
        
        assignment = Assignment(
            report_id=report_id,
            officer_id=officer_id,
            assigned_by=assigned_by,
            status=status,
            notes=fake.text(max_nb_chars=150),
            response_time=fake.random_int(min=300, max=3600) if status == 'COMPLETED' else None
        )
        
        return assignment

class LocationFactory:
    @staticmethod
    def create(user_id):
        """Create GPS location for user"""
        # Koordinat sekitar Indonesia
        indonesia_lat = fake.latitude(min=-11, max=6)
        indonesia_lng = fake.longitude(min=95, max=141)
        
        return Location(
            user_id=user_id,
            latitude=indonesia_lat,
            longitude=indonesia_lng,
            accuracy=fake.random_int(min=5, max=50),
            is_active=random.choice([True, False])
        )
    
    @staticmethod
    def create_trail(user_id, count=10):
        """Create location trail for user"""
        locations = []
        base_lat = fake.latitude(min=-11, max=6)
        base_lng = fake.longitude(min=95, max=141)
        
        for i in range(count):
            # Simulate movement dengan variasi kecil
            lat_variation = random.uniform(-0.01, 0.01)
            lng_variation = random.uniform(-0.01, 0.01)
            
            location = Location(
                user_id=user_id,
                latitude=base_lat + lat_variation,
                longitude=base_lng + lng_variation,
                accuracy=fake.random_int(min=5, max=50),
                is_active=i == 0  # Only first location is active
            )
            locations.append(location)
            
            # Update base position
            base_lat += lat_variation
            base_lng += lng_variation
        
        return locations

class TimelineEventFactory:
    @staticmethod
    def create(report_id, created_by):
        """Create timeline event for report"""
        event_types = [
            'report_created', 'status_changed', 'assignment_created',
            'evidence_added', 'officer_assigned', 'investigation_started',
            'case_resolved', 'false_alarm_marked'
        ]
        
        event_type = random.choice(event_types)
        
        event_data = {
            'event_type': event_type,
            'description': fake.sentence(),
            'timestamp': fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
            'additional_info': fake.text(max_nb_chars=100)
        }
        
        return TimelineEvent(
            report_id=report_id,
            event_type=event_type,
            event_data=event_data,
            created_by=created_by
        )
    
    @staticmethod
    def create_report_timeline(report_id, created_by, status_flow=None):
        """Create complete timeline for a report"""
        events = []
        
        # Default status flow
        if not status_flow:
            status_flow = ['report_created', 'status_changed', 'officer_assigned', 
                          'investigation_started', 'case_resolved']
        
        for event_type in status_flow:
            event_data = {
                'event_type': event_type,
                'description': f"{event_type.replace('_', ' ').capitalize()} - {fake.sentence()}",
                'timestamp': fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
                'additional_info': fake.text(max_nb_chars=100)
            }
            
            event = TimelineEvent(
                report_id=report_id,
                event_type=event_type,
                event_data=event_data,
                created_by=created_by
            )
            events.append(event)
        
        return events

class NotificationFactory:
    @staticmethod
    def create_weapon_detection(user_id, reference_id):
        """Create weapon detection notification"""
        weapon_types = ['pisau', 'senjata api', 'parang', 'pedang']
        weapon = random.choice(weapon_types)
        
        return Notification(
            user_id=user_id,
            title="🚨 DETEKSI SENJATA!",
            message=f"Sistem mendeteksi {weapon} di lokasi Anda. Mohon segera periksa dan laporkan ke pihak berwajib.",
            notification_type='emergency',  # Fixed: lowercase to match enum
            reference_id=reference_id,
            is_read=random.choice([True, False])
        )
    
    @staticmethod
    def create_assignment(user_id, reference_id):
        """Create assignment notification"""
        return Notification(
            user_id=user_id,
            title="📋 Penugasan Baru",
            message=f"Anda mendapat penugasan baru. Mohon segera cek dan konfirmasi penerimaan tugas.",
            notification_type='assignment',  # Fixed: lowercase to match enum
            reference_id=reference_id,
            is_read=random.choice([True, False])
        )
    
    @staticmethod
    def create_system_alert(user_id):
        """Create system alert notification"""
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
            notification_type='system',  # Fixed: lowercase to match enum
            reference_id=None,
            is_read=random.choice([True, False])
        )
    
    @staticmethod
    def create_report_notification(user_id, reference_id):
        """Create report notification"""
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
            notification_type='report',  # Fixed: lowercase to match enum
            reference_id=reference_id,
            is_read=random.choice([True, False])
        )

class ReportUpdateFactory:
    @staticmethod
    def create(report_id, user_id):
        """Create report update"""
        status_changes = ['NEW', 'VERIFIED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FALSE_ALARM']
        
        updates = [
            "Laporan telah diverifikasi oleh admin",
            "Petugas telah ditugaskan untuk menangani kasus ini",
            "Investigasi sedang berlangsung",
            "Kasus telah diselesaikan dengan baik",
            "Ternyata ini adalah alarm palsu",
            "Memerlukan bukti tambahan untuk investigasi"
        ]
        
        return ReportUpdate(
            report_id=report_id,
            user_id=user_id,
            content=random.choice(updates),
            status_change=random.choice(status_changes) if random.random() > 0.5 else None
        )
    
    @staticmethod
    def create_multiple(report_id, user_id, count=3):
        """Create multiple updates for a report"""
        updates = []
        for _ in range(count):
            updates.append(ReportUpdateFactory.create(report_id, user_id))
        return updates

class PerformanceMetricFactory:
    @staticmethod
    def create(user_id):
        """Create performance metric for user"""
        metric_types = [
            'response_time', 'completion_rate', 'accuracy_rate',
            'cases_resolved', 'false_alarm_rate', 'customer_satisfaction'
        ]
        
        metric_type = random.choice(metric_types)
        
        # Generate nilai yang masuk akal berdasarkan metric type
        if metric_type == 'response_time':
            value = fake.random_int(min=300, max=1800)  # seconds
        elif metric_type in ['completion_rate', 'accuracy_rate', 'customer_satisfaction']:
            value = round(random.uniform(0.7, 0.98), 2)  # percentage
        elif metric_type == 'cases_resolved':
            value = fake.random_int(min=5, max=50)  # count
        elif metric_type == 'false_alarm_rate':
            value = round(random.uniform(0.05, 0.25), 2)  # percentage
        else:
            value = round(random.uniform(0.1, 1.0), 2)
        
        start_date = fake.date_time_between(start_date='-30d', end_date='-1d')
        end_date = start_date + timedelta(days=7)
        
        return PerformanceMetric(
            user_id=user_id,
            metric_type=metric_type,
            value=value,
            period_start=start_date,
            period_end=end_date
        )
    
    @staticmethod
    def create_user_metrics(user_id):
        """Create complete set of metrics for a user"""
        metric_types = [
            'response_time', 'completion_rate', 'accuracy_rate',
            'cases_resolved', 'false_alarm_rate', 'customer_satisfaction'
        ]
        
        metrics = []
        start_date = fake.date_time_between(start_date='-30d', end_date='-1d')
        end_date = start_date + timedelta(days=7)
        
        for metric_type in metric_types:
            # Generate appropriate values
            if metric_type == 'response_time':
                value = fake.random_int(min=300, max=1800)
            elif metric_type in ['completion_rate', 'accuracy_rate', 'customer_satisfaction']:
                value = round(random.uniform(0.7, 0.98), 2)
            elif metric_type == 'cases_resolved':
                value = fake.random_int(min=5, max=50)
            elif metric_type == 'false_alarm_rate':
                value = round(random.uniform(0.05, 0.25), 2)
            else:
                value = round(random.uniform(0.1, 1.0), 2)
            
            metric = PerformanceMetric(
                user_id=user_id,
                metric_type=metric_type,
                value=value,
                period_start=start_date,
                period_end=end_date
            )
            metrics.append(metric)
        
        return metrics

class TokenBlacklistFactory:
    @staticmethod
    def create(user_id):
        """Create blacklisted token"""
        return TokenBlacklist(
            jti=str(uuid.uuid4()),
            token_type=random.choice(['access', 'refresh']),
            user_id=user_id,
            revoked=True,
            expires=fake.date_time_between(start_date='now', end_date='+30d')
        )

# Helper class untuk complete data seeding
class DatabaseSeeder:
    """Helper class to seed complete database with related data"""
    
    @staticmethod
    def seed_complete_system(num_admins=2, num_officers=10, num_owners=20, 
                           cameras_per_owner=3, reports_per_camera=5):
        """Seed complete system with all related data"""
        
        # Lists to store created entities
        users = []
        cameras = []
        reports = []
        
        print("🌱 Starting database seeding...")
        
        # 1. Create Users
        print("👥 Creating users...")
        # Admins
        for i in range(num_admins):
            admin = UserFactory.create_admin(
                email=f"admin{i+1}@example.com",
                name=f"Admin {i+1}"
            )
            users.append(admin)
            db.session.add(admin)
        
        # Officers
        for i in range(num_officers):
            officer = UserFactory.create_officer(
                email=f"officer{i+1}@example.com",
                name=f"Officer {i+1}"
            )
            users.append(officer)
            db.session.add(officer)
        
        # Owners
        for i in range(num_owners):
            owner = UserFactory.create_owner(
                email=f"owner{i+1}@example.com",
                name=f"Owner {i+1}"
            )
            users.append(owner)
            db.session.add(owner)
        
        db.session.commit()
        print(f"✅ Created {len(users)} users")
        
        # 2. Create Cameras for Owners
        print("📹 Creating cameras...")
        owners = [u for u in users if u.role.value == 'owner']
        for owner in owners:
            for _ in range(cameras_per_owner):
                camera = CameraFactory.create(owner.id)
                cameras.append(camera)
                db.session.add(camera)
        
        db.session.commit()
        print(f"✅ Created {len(cameras)} cameras")
        
        # 3. Create Reports
        print("📋 Creating reports...")
        for camera in cameras:
            # Mix of manual and automatic reports
            for i in range(reports_per_camera):
                if random.random() > 0.3:  # 70% manual reports
                    report = ReportFactory.create_manual(
                        camera_id=camera.id,
                        reporter_id=camera.owner_id
                    )
                else:  # 30% automatic reports
                    report = ReportFactory.create_automatic(
                        camera_id=camera.id,
                        reporter_id=camera.owner_id
                    )
                reports.append(report)
                db.session.add(report)
        
        db.session.commit()
        print(f"✅ Created {len(reports)} reports")
        
        # 4. Create Assignments for some reports
        print("📝 Creating assignments...")
        officers = [u for u in users if u.role.value == 'officer']
        admins = [u for u in users if u.role.value == 'admin']
        assigned_reports = random.sample(reports, min(len(reports) // 2, 50))
        
        for report in assigned_reports:
            if officers and admins:
                assignment = AssignmentFactory.create(
                    report_id=report.id,
                    officer_id=random.choice(officers).id,
                    assigned_by=random.choice(admins).id
                )
                db.session.add(assignment)
        
        db.session.commit()
        print(f"✅ Created assignments for {len(assigned_reports)} reports")
        
        # 5. Create Evidence for some reports
        print("🗂️ Creating evidence...")
        evidence_reports = random.sample(reports, min(len(reports) // 3, 30))
        for report in evidence_reports:
            evidences = EvidenceFactory.create_multiple(
                report_id=report.id,
                created_by=report.reporter_id,
                count=random.randint(1, 5)
            )
            for evidence in evidences:
                db.session.add(evidence)
        
        db.session.commit()
        print(f"✅ Created evidence for {len(evidence_reports)} reports")
        
        # 6. Create Timeline Events
        print("⏱️ Creating timeline events...")
        for report in reports[:20]:  # Create for first 20 reports
            events = TimelineEventFactory.create_report_timeline(
                report_id=report.id,
                created_by=report.reporter_id
            )
            for event in events:
                db.session.add(event)
        
        db.session.commit()
        print("✅ Created timeline events")
        
        # 7. Create Notifications
        print("🔔 Creating notifications...")
        # Weapon detection notifications for owners
        for report in [r for r in reports if r.is_automatic]:
            notif = NotificationFactory.create_weapon_detection(
                user_id=report.reporter_id,
                reference_id=report.id
            )
            db.session.add(notif)
        
        # Assignment notifications for officers
        for assignment in db.session.query(Assignment).all():
            notif = NotificationFactory.create_assignment(
                user_id=assignment.officer_id,
                reference_id=assignment.id
            )
            db.session.add(notif)
        
        db.session.commit()
        print("✅ Created notifications")
        
        # 8. Create Location data for officers
        print("📍 Creating location data...")
        for officer in officers:
            locations = LocationFactory.create_trail(officer.id, count=5)
            for location in locations:
                db.session.add(location)
        
        db.session.commit()
        print("✅ Created location data")
        
        # 9. Create Performance Metrics
        print("📊 Creating performance metrics...")
        for officer in officers:
            metrics = PerformanceMetricFactory.create_user_metrics(officer.id)
            for metric in metrics:
                db.session.add(metric)
        
        db.session.commit()
        print("✅ Created performance metrics")
        
        # 10. Create some Report Updates
        print("🔄 Creating report updates...")
        for report in reports[:15]:
            updates = ReportUpdateFactory.create_multiple(
                report_id=report.id,
                user_id=random.choice(admins).id if admins else report.reporter_id,
                count=random.randint(1, 3)
            )
            for update in updates:
                db.session.add(update)
        
        db.session.commit()
        print("✅ Created report updates")
        
        print("\n🎉 Database seeding completed successfully!")
        print(f"""
        Summary:
        - Users: {len(users)} ({num_admins} admins, {num_officers} officers, {num_owners} owners)
        - Cameras: {len(cameras)}
        - Reports: {len(reports)}
        - Assignments: {len(assigned_reports)}
        - Plus evidence, notifications, locations, metrics, etc.
        """)
        
        return {
            'users': users,
            'cameras': cameras,
            'reports': reports
        }