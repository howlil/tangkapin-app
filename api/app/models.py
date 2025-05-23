from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import uuid
import json
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy import event, Index
from app.utils.logger import logger

db = SQLAlchemy()

# Enums untuk status dan priority
class UserRole(enum.Enum):
    ADMIN = "admin"
    OFFICER = "officer"
    OWNER = "owner"

class CameraStatus(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class ReportStatus(enum.Enum):
    NEW = "NEW"
    VERIFIED = "VERIFIED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FALSE_ALARM = "FALSE_ALARM"

class ReportPriority(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AssignmentStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"

class EvidenceType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"

class NotificationType(enum.Enum):
    REPORT = "report"
    ASSIGNMENT = "assignment"
    SYSTEM = "system"
    EMERGENCY = "emergency"

# Model Users
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False, index=True)
    badge_number = db.Column(db.String(50), nullable=True)  # Untuk officers
    longitude = db.Column(db.String(20), nullable=True)  # Longitude coordinate
    latitude = db.Column(db.String(20), nullable=True)   # Latitude coordinate
    fcm_token = db.Column(db.String(255), nullable=True)  # Firebase Cloud Messaging
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    cameras = db.relationship('Camera', back_populates='owner', lazy='dynamic', cascade='all, delete-orphan')
    reports_created = db.relationship('Report', foreign_keys='Report.reporter_id', back_populates='reporter', lazy='dynamic')
    assignments = db.relationship('Assignment', foreign_keys='Assignment.officer_id', back_populates='officer', lazy='dynamic')
    assignments_created = db.relationship('Assignment', foreign_keys='Assignment.assigned_by', back_populates='admin', lazy='dynamic')
    locations = db.relationship('Location', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    evidences_created = db.relationship('Evidence', back_populates='creator', lazy='dynamic')
    timeline_events = db.relationship('TimelineEvent', back_populates='creator', lazy='dynamic')
    report_updates = db.relationship('ReportUpdate', back_populates='user', lazy='dynamic')
    performance_metrics = db.relationship('PerformanceMetric', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'role': self.role.value if self.role else None,
            'badge_number': self.badge_number,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Model Camera (CCTV)
class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    stream_url = db.Column(db.String(255), nullable=False)
    cctv_ip = db.Column(db.String(255), nullable=True)  # IP address kamera
    status = db.Column(db.Enum(CameraStatus), default=CameraStatus.OFFLINE, nullable=False, index=True)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    last_online = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = db.relationship('User', back_populates='cameras')
    reports = db.relationship('Report', back_populates='camera', lazy='dynamic')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'stream_url': self.stream_url,
            'cctv_ip': self.cctv_ip,
            'status': self.status.value if self.status else None,
            'owner_id': self.owner_id,
            'is_active': self.is_active,
            'last_online': self.last_online.isoformat() if self.last_online else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Model Report
class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    camera_id = db.Column(db.String(36), db.ForeignKey('cameras.id', ondelete='CASCADE'), nullable=False, index=True)
    reporter_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.Enum(ReportStatus), default=ReportStatus.NEW, nullable=False, index=True)
    priority = db.Column(db.Enum(ReportPriority), default=ReportPriority.MEDIUM, nullable=False, index=True)
    detection_confidence = db.Column(db.Float, nullable=True)  # Untuk ML detections
    weapon_type = db.Column(db.String(50), nullable=True)  # Jenis senjata yang terdeteksi
    detection_image_url = db.Column(db.String(500), nullable=True)  # URL gambar deteksi
    is_automatic = db.Column(db.Boolean, default=False, nullable=False, index=True)  # True jika dari ML
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    camera = db.relationship('Camera', back_populates='reports')
    reporter = db.relationship('User', foreign_keys=[reporter_id], back_populates='reports_created')
    evidences = db.relationship('Evidence', back_populates='report', lazy='dynamic', cascade='all, delete-orphan')
    timeline_events = db.relationship('TimelineEvent', back_populates='report', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', back_populates='report', lazy='dynamic', cascade='all, delete-orphan')
    report_updates = db.relationship('ReportUpdate', back_populates='report', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'camera_id': self.camera_id,
            'reporter_id': self.reporter_id,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'detection_confidence': self.detection_confidence,
            'weapon_type': self.weapon_type,
            'detection_image_url': self.detection_image_url,
            'is_automatic': self.is_automatic,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Model Evidence
class Evidence(db.Model):
    __tablename__ = 'evidences'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False, index=True)
    file_url = db.Column(db.String(500), nullable=False)  # URL file di storage
    file_type = db.Column(db.Enum(EvidenceType), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    report = db.relationship('Report', back_populates='evidences')
    creator = db.relationship('User', back_populates='evidences_created')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'file_url': self.file_url,
            'file_type': self.file_type.value if self.file_type else None,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Model Assignment
class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False, index=True)
    officer_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    assigned_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Enum(AssignmentStatus), default=AssignmentStatus.PENDING, nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    response_time = db.Column(db.Integer, nullable=True)  # Waktu respons dalam detik
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    report = db.relationship('Report', back_populates='assignments')
    officer = db.relationship('User', foreign_keys=[officer_id], back_populates='assignments')
    admin = db.relationship('User', foreign_keys=[assigned_by], back_populates='assignments_created')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'officer_id': self.officer_id,
            'assigned_by': self.assigned_by,
            'status': self.status.value if self.status else None,
            'notes': self.notes,
            'response_time': self.response_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Model Location (GPS Tracking)
class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)  # Akurasi dalam meter
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='locations')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Model Timeline Event
class TimelineEvent(db.Model):
    __tablename__ = 'timeline_events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)  # status_change, assignment, evidence_added, etc.
    event_data = db.Column(db.JSON, nullable=False)  # Data tambahan event dalam format JSON
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    report = db.relationship('Report', back_populates='timeline_events')
    creator = db.relationship('User', back_populates='timeline_events')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }

# Model Notification
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    notification_type = db.Column(db.Enum(NotificationType), nullable=False, index=True)
    reference_id = db.Column(db.String(36), nullable=True)  # ID entitas terkait (report, assignment, etc.)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'reference_id': self.reference_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }

# Model Report Update
class ReportUpdate(db.Model):
    __tablename__ = 'report_updates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status_change = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    report = db.relationship('Report', back_populates='report_updates')
    user = db.relationship('User', back_populates='report_updates')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'report_id': self.report_id,
            'user_id': self.user_id,
            'content': self.content,
            'status_change': self.status_change,
            'created_at': self.created_at.isoformat()
        }

# Model Performance Metric
class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    metric_type = db.Column(db.String(50), nullable=False)  # response_time, completion_rate, etc.
    value = db.Column(db.Float, nullable=False)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='performance_metrics')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'metric_type': self.metric_type,
            'value': self.value,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'created_at': self.created_at.isoformat()
        }

# Model Token Blacklist (untuk JWT security)
class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, index=True)  # JWT ID
    token_type = db.Column(db.String(10), nullable=False)  # access atau refresh
    user_id = db.Column(db.String(36), nullable=False)
    revoked = db.Column(db.Boolean, default=True, nullable=False)
    expires = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_id': self.user_id,
            'revoked': self.revoked,
            'expires': self.expires.isoformat(),
            'created_at': self.created_at.isoformat()
        }

# Model DetectionLog
class DetectionLog(db.Model):
    __tablename__ = 'detection_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    camera_id = db.Column(db.String(36), db.ForeignKey('cameras.id', ondelete='CASCADE'), nullable=False, index=True)
    weapon_detected = db.Column(db.Boolean, default=False, nullable=False, index=True)
    weapon_type = db.Column(db.String(50), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    frame_data = db.Column(db.Text, nullable=True)  # Base64 encoded frame
    processing_time = db.Column(db.Float, nullable=True)  # Time taken to process in seconds
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, detected, error
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    camera = db.relationship('Camera', backref=db.backref('detection_logs', lazy='dynamic'))
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'weapon_detected': self.weapon_detected,
            'weapon_type': self.weapon_type,
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }

# Utility functions
def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

def create_indexes(app):
    """Create additional indexes for performance optimization"""
    with app.app_context():
        try:
            # Composite indexes untuk query yang sering digunakan
            db.engine.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_owner_created 
                ON reports(reporter_id, created_at DESC);
            ''')
            
            db.engine.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_camera_status 
                ON reports(camera_id, status);
            ''')
            
            db.engine.execute('''
                CREATE INDEX IF NOT EXISTS idx_assignments_officer_status 
                ON assignments(officer_id, status);
            ''')
            
            db.engine.execute('''
                CREATE INDEX IF NOT EXISTS idx_locations_user_created 
                ON locations(user_id, created_at DESC);
            ''')
            
            db.engine.execute('''
                CREATE INDEX IF NOT EXISTS idx_notifications_user_read 
                ON notifications(user_id, is_read, created_at DESC);
            ''')
            
            db.engine.execute('''
                CREATE INDEX IF NOT EXISTS idx_cameras_owner_status 
                ON cameras(owner_id, status, is_active);
            ''')
            
            logger.logger.info("Additional indexes created successfully")
            
        except Exception as e:
            logger.logger.error(f"Error creating indexes: {e}")

# Create additional indexes after table creation
@event.listens_for(db.metadata, 'after_create')
def create_indexes(target, connection, **kwargs):
    try:
        # Create optimized indexes for common queries
        connection.execute('CREATE INDEX idx_detectionlog_camera_id ON detection_logs (camera_id)')
        connection.execute('CREATE INDEX idx_detectionlog_created_at ON detection_logs (created_at)')
        connection.execute('CREATE INDEX idx_detectionlog_weapon_detected ON detection_logs (weapon_detected)')
        
        # Compound indexes for common query patterns
        connection.execute('CREATE INDEX idx_camera_active_ml ON cameras (is_active, ml_enabled)')
        connection.execute('CREATE INDEX idx_notification_status_retry ON notifications (status, retry_count)')
        
        logger.logger.info("Additional indexes created successfully")
    except Exception as e:
        logger.logger.error(f"Error creating indexes: {e}")

RoleEnum = UserRole
CCTV = Camera  # Alias untuk model CCTV yang digunakan di kode lama