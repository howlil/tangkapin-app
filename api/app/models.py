from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import uuid

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
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # admin, officer, owner
    badge_number = db.Column(db.String(50), nullable=True)  # For officers
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cameras = db.relationship('Camera', back_populates='owner', lazy='dynamic')
    reports_created = db.relationship('Report', foreign_keys='Report.reporter_id', back_populates='reporter', lazy='dynamic')
    assignments = db.relationship('Assignment', foreign_keys='Assignment.officer_id', back_populates='officer', lazy='dynamic')
    locations = db.relationship('Location', back_populates='user', lazy='dynamic')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'role': self.role,
            'badge_number': self.badge_number,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Model Camera (disederhanakan untuk IP webcam)
class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    stream_url = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='offline')  # online, offline, maintenance
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_online = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = db.relationship('User', back_populates='cameras')
    reports = db.relationship('Report', back_populates='camera', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'stream_url': self.stream_url,
            'status': self.status,
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
    camera_id = db.Column(db.String(36), db.ForeignKey('cameras.id'), nullable=False)
    reporter_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='NEW')  # NEW, VERIFIED, ASSIGNED, IN_PROGRESS, COMPLETED, FALSE_ALARM
    priority = db.Column(db.String(20), default='MEDIUM')  # LOW, MEDIUM, HIGH, CRITICAL
    detection_confidence = db.Column(db.Float, nullable=True)  # For ML detections
    weapon_type = db.Column(db.String(50), nullable=True)  # For ML detections
    detection_image_url = db.Column(db.String(255), nullable=True)  # URL to image in Supabase storage
    is_automatic = db.Column(db.Boolean, default=False)  # True if created by ML, False if manually created
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    camera = db.relationship('Camera', back_populates='reports')
    reporter = db.relationship('User', foreign_keys=[reporter_id], back_populates='reports_created')
    evidences = db.relationship('Evidence', back_populates='report', lazy='dynamic')
    timeline_events = db.relationship('TimelineEvent', back_populates='report', lazy='dynamic')
    assignments = db.relationship('Assignment', back_populates='report', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'camera_id': self.camera_id,
            'reporter_id': self.reporter_id,
            'status': self.status,
            'priority': self.priority,
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
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id'), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)  # URL to file in Supabase storage
    file_type = db.Column(db.String(20), nullable=False)  # image, video, audio, document
    description = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    report = db.relationship('Report', back_populates='evidences')
    user = db.relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Model Timeline Event
class TimelineEvent(db.Model):
    __tablename__ = 'timeline_events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # status_change, assignment, evidence_added, note_added
    event_data = db.Column(db.JSON, nullable=False)  # Store additional event-specific data
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    report = db.relationship('Report', back_populates='timeline_events')
    user = db.relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }

# Model Assignment (Penugasan Officer)
class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id'), nullable=False)
    officer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, ACCEPTED, IN_PROGRESS, COMPLETED, REJECTED
    assigned_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    response_time = db.Column(db.Integer, nullable=True)  # Time in seconds to respond
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    report = db.relationship('Report', back_populates='assignments')
    officer = db.relationship('User', foreign_keys=[officer_id], back_populates='assignments')
    admin = db.relationship('User', foreign_keys=[assigned_by], backref='assignments_created')
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'officer_id': self.officer_id,
            'status': self.status,
            'assigned_by': self.assigned_by,
            'notes': self.notes,
            'response_time': self.response_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Model Location (Live tracking)
class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='locations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Model Notification
class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # report, assignment, system
    reference_id = db.Column(db.String(36), nullable=True)  # ID of the related entity (report, assignment, etc.)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'reference_id': self.reference_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }

# Model ReportUpdate
class ReportUpdate(db.Model):
    __tablename__ = 'report_updates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = db.Column(db.String(36), db.ForeignKey('reports.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status_change = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    report = db.relationship('Report')
    user = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'user_id': self.user_id,
            'content': self.content,
            'status_change': self.status_change,
            'created_at': self.created_at.isoformat()
        }

# Model PerformanceMetric
class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # response_time, completion_rate, report_accuracy
    value = db.Column(db.Float, nullable=False)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'metric_type': self.metric_type,
            'value': self.value,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'created_at': self.created_at.isoformat()
        }

# Model Token Blacklist
class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    revoked = db.Column(db.Boolean, default=True)
    expires = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_id': self.user_id,
            'revoked': self.revoked,
            'expires': self.expires.isoformat(),
            'created_at': self.created_at.isoformat()
        }

# Utility function untuk inisialisasi database
def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
def create_indexes():
    """Create database indexes for performance optimization"""
    try:
        # Indexes untuk query yang sering digunakan
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_reports_owner_created ON reports(owner_id, created_at);')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_reports_priority ON reports(priority);')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_locations_user_current ON locations(user_id, is_current);')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_assignments_officer_status ON assignments(officer_id, status);')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);')
        db.engine.execute('CREATE INDEX IF NOT EXISTS idx_cameras_owner_status ON cameras(owner_id, status);')
    except Exception as e:
        print(f"Error creating indexes: {e}")