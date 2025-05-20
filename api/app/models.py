from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

# Enums untuk status dan priority
class UserRole(enum.Enum):
    ADMIN = "admin"
    OFFICER = "officer"
    OWNER = "owner"

class ReportStatus(enum.Enum):
    NEW = "new"
    VERIFIED = "verified"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FALSE_ALARM = "false_alarm"

class ReportPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CameraStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class AssignmentStatus(enum.Enum):
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"

# Model Users
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    badge_number = db.Column(db.String(50), nullable=True)  # Untuk officer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owned_cameras = db.relationship('Camera', backref='owner', lazy=True)
    reports_created = db.relationship('Report', foreign_keys='Report.owner_id', backref='owner', lazy=True)
    assignments = db.relationship('Assignment', foreign_keys='Assignment.officer_id', backref='officer', lazy=True)
    admin_assignments = db.relationship('Assignment', foreign_keys='Assignment.admin_id', backref='admin', lazy=True)
    locations = db.relationship('Location', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role.value,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'badge_number': self.badge_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Model Camera (disederhanakan untuk IP webcam)
class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # Mendukung IPv4 dan IPv6
    port = db.Column(db.Integer, default=8080)  # Port untuk IP webcam
    username = db.Column(db.String(50), nullable=True)  # Untuk authentication
    password = db.Column(db.String(100), nullable=True)  # Untuk authentication
    location_name = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    status = db.Column(db.Enum(CameraStatus), default=CameraStatus.OFFLINE)
    is_active = db.Column(db.Boolean, default=True)
    stream_url = db.Column(db.String(500), nullable=True)  # URL stream lengkap
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_ping = db.Column(db.DateTime, nullable=True)  # Terakhir kali camera online
    
    # Relationships
    reports = db.relationship('Report', backref='camera', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'ip_address': self.ip_address,
            'port': self.port,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status.value,
            'is_active': self.is_active,
            'stream_url': self.stream_url,
            'last_ping': self.last_ping.isoformat() if self.last_ping else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Model Report
class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(50), default='weapon_detection')
    status = db.Column(db.Enum(ReportStatus), default=ReportStatus.NEW)
    priority = db.Column(db.Enum(ReportPriority), default=ReportPriority.MEDIUM)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # ML Detection Results
    detection_confidence = db.Column(db.Float, nullable=True)  # Confidence score
    detection_results = db.Column(db.JSON, nullable=True)  # JSON hasil deteksi ML
    
    # Location Information
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(500), nullable=True)
    
    # Evidence
    image_path = db.Column(db.String(500), nullable=True)  # Path gambar bukti
    video_path = db.Column(db.String(500), nullable=True)  # Path video bukti
    additional_evidence = db.Column(db.JSON, nullable=True)  # Evidence tambahan
    
    # Timestamps
    incident_datetime = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Admin notes
    admin_notes = db.Column(db.Text, nullable=True)
    verification_notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='report', lazy=True)
    report_updates = db.relationship('ReportUpdate', backref='report', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'owner_id': self.owner_id,
            'report_type': self.report_type,
            'status': self.status.value,
            'priority': self.priority.value,
            'title': self.title,
            'description': self.description,
            'detection_confidence': self.detection_confidence,
            'detection_results': self.detection_results,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'image_path': self.image_path,
            'video_path': self.video_path,
            'incident_datetime': self.incident_datetime.isoformat() if self.incident_datetime else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

# Model Assignment (Penugasan Officer)
class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(AssignmentStatus), default=AssignmentStatus.ASSIGNED)
    
    # Timing
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    arrived_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Location tracking
    distance_km = db.Column(db.Float, nullable=True)
    estimated_arrival = db.Column(db.DateTime, nullable=True)
    
    # Notes
    assignment_notes = db.Column(db.Text, nullable=True)
    completion_notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'officer_id': self.officer_id,
            'admin_id': self.admin_id,
            'status': self.status.value,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'arrived_at': self.arrived_at.isoformat() if self.arrived_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'distance_km': self.distance_km,
            'estimated_arrival': self.estimated_arrival.isoformat() if self.estimated_arrival else None
        }

# Model Location (Live tracking)
class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(500), nullable=True)
    accuracy = db.Column(db.Float, nullable=True)  # GPS accuracy in meters
    is_current = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'accuracy': self.accuracy,
            'is_current': self.is_current,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Model Report Update (Timeline status)
class ReportUpdate(db.Model):
    __tablename__ = 'report_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    update_type = db.Column(db.String(50), nullable=False)  # status_change, note, evidence
    old_value = db.Column(db.String(100), nullable=True)
    new_value = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='report_updates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'user_id': self.user_id,
            'update_type': self.update_type,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.name if self.user else None
        }

# Model Notification
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # new_report, assignment, status_update
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    report = db.relationship('Report', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_id': self.report_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

# Model untuk menyimpan performance metrics
class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    response_time_minutes = db.Column(db.Float, nullable=True)  # Waktu respons dalam menit
    resolution_time_hours = db.Column(db.Float, nullable=True)  # Waktu penyelesaian dalam jam
    distance_traveled_km = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    officer = db.relationship('User', backref='performance_metrics')
    report = db.relationship('Report', backref='performance_metric')
    
    def to_dict(self):
        return {
            'id': self.id,
            'officer_id': self.officer_id,
            'report_id': self.report_id,
            'response_time_minutes': self.response_time_minutes,
            'resolution_time_hours': self.resolution_time_hours,
            'distance_traveled_km': self.distance_traveled_km,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Utility function untuk inisialisasi database
def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
def create_indexes():
    """Create database indexes for performance optimization"""
    # Indexes untuk query yang sering digunakan
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_reports_owner_created ON reports(owner_id, created_at);')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_reports_priority ON reports(priority);')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_locations_user_current ON locations(user_id, is_current);')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_assignments_officer_status ON assignments(officer_id, status);')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_cameras_owner_status ON cameras(owner_id, status);')