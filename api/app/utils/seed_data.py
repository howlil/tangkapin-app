import uuid
from datetime import datetime, timedelta
from random import choice, uniform, randint
from app import db
from app.models import User, Camera, Report, Evidence, TimelineEvent, Assignment, Location, Notification

def seed_database():
    """Seed the database with sample data."""
    # Create users
    admin = create_user('admin@tangkapin.com', 'Admin User', 'admin', 'admin123')
    officers = [
        create_user('officer1@tangkapin.com', 'Officer One', 'officer', 'officer123', badge_number='OFF001'),
        create_user('officer2@tangkapin.com', 'Officer Two', 'officer', 'officer123', badge_number='OFF002'),
        create_user('officer3@tangkapin.com', 'Officer Three', 'officer', 'officer123', badge_number='OFF003')
    ]
    owners = [
        create_user('owner1@tangkapin.com', 'Store Owner One', 'owner', 'owner123'),
        create_user('owner2@tangkapin.com', 'Store Owner Two', 'owner', 'owner123')
    ]
    
    # Create cameras
    cameras = []
    for i, owner in enumerate(owners):
        for j in range(2):
            cameras.append(create_camera(
                f'Camera {i+1}-{j+1}',
                f'Store {i+1} - Camera {j+1}',
                f'Jalan Example No. {randint(1, 100)}, Jakarta',
                f'rtsp://example.com/store{i+1}/camera{j+1}',
                owner.id
            ))
    
    # Create reports
    reports = []
    for i, camera in enumerate(cameras):
        reports.append(create_report(
            f'Suspicious Activity Report {i+1}',
            f'Detected suspicious activity in store {i+1}',
            camera.id,
            camera.owner_id,
            is_automatic=True,
            weapon_type='Knife',
            detection_confidence=uniform(0.75, 0.98)
        ))
    
    # Create manual report
    reports.append(create_report(
        'Manual Emergency Report',
        'Store owner reported armed robbery in progress',
        cameras[0].id,
        owners[0].id,
        is_automatic=False,
        status='VERIFIED',
        priority='HIGH'
    ))
    
    # Create evidences
    for report in reports:
        create_evidence(
            report.id,
            'https://supabase.example.com/storage/evidences/image1.jpg',
            'image',
            'Detection image',
            report.reporter_id
        )
    
    # Create assignments
    for report in reports[:3]:
        create_assignment(
            report.id,
            officers[0].id,
            admin.id,
            'PENDING',
            'Please investigate this report immediately'
        )
    
    # Create in-progress assignment
    create_assignment(
        reports[3].id,
        officers[1].id,
        admin.id,
        'IN_PROGRESS',
        'Officer responding to scene'
    )
    
    # Create timeline events
    for report in reports:
        create_timeline_event(
            report.id,
            'status_change',
            {'old_status': None, 'new_status': report.status},
            report.reporter_id
        )
    
    # Create locations for officers
    for officer in officers:
        create_location(
            officer.id,
            uniform(-6.1, -6.3),  # Jakarta latitude range
            uniform(106.7, 106.9)  # Jakarta longitude range
        )
    
    # Create notifications
    for owner in owners:
        create_notification(
            owner.id,
            'Camera Offline',
            'One of your cameras has gone offline',
            'system',
            cameras[0].id
        )
    
    for officer in officers:
        create_notification(
            officer.id,
            'New Assignment',
            'You have been assigned to a new report',
            'assignment',
            reports[0].id
        )
    
    db.session.commit()


def create_user(email, name, role, password, **kwargs):
    """Create a user and return the instance."""
    user = User.query.filter_by(email=email).first()
    if user:
        return user
        
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        name=name,
        role=role,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        **kwargs
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def create_camera(name, description, location, stream_url, owner_id):
    """Create a camera and return the instance."""
    camera = Camera(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        location=location,
        latitude=uniform(-6.1, -6.3),  # Jakarta latitude range
        longitude=uniform(106.7, 106.9),  # Jakarta longitude range
        stream_url=stream_url,
        status=choice(['online', 'offline']),
        owner_id=owner_id,
        is_active=True,
        last_online=datetime.utcnow() - timedelta(minutes=randint(0, 60)),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(camera)
    db.session.flush()
    return camera


def create_report(title, description, camera_id, reporter_id, is_automatic=False, **kwargs):
    """Create a report and return the instance."""
    status = kwargs.get('status', 'NEW')
    priority = kwargs.get('priority', 'MEDIUM')
    weapon_type = kwargs.get('weapon_type', None)
    detection_confidence = kwargs.get('detection_confidence', None)
    
    report = Report(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        camera_id=camera_id,
        reporter_id=reporter_id,
        status=status,
        priority=priority,
        is_automatic=is_automatic,
        weapon_type=weapon_type,
        detection_confidence=detection_confidence,
        detection_image_url='https://supabase.example.com/storage/detections/image1.jpg' if is_automatic else None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(report)
    db.session.flush()
    return report


def create_evidence(report_id, file_url, file_type, description, created_by):
    """Create evidence and return the instance."""
    evidence = Evidence(
        id=str(uuid.uuid4()),
        report_id=report_id,
        file_url=file_url,
        file_type=file_type,
        description=description,
        created_by=created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(evidence)
    db.session.flush()
    return evidence


def create_assignment(report_id, officer_id, assigned_by, status, notes):
    """Create an assignment and return the instance."""
    assignment = Assignment(
        id=str(uuid.uuid4()),
        report_id=report_id,
        officer_id=officer_id,
        assigned_by=assigned_by,
        status=status,
        notes=notes,
        response_time=randint(60, 300) if status != 'PENDING' else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(assignment)
    db.session.flush()
    return assignment


def create_timeline_event(report_id, event_type, event_data, created_by):
    """Create a timeline event and return the instance."""
    event = TimelineEvent(
        id=str(uuid.uuid4()),
        report_id=report_id,
        event_type=event_type,
        event_data=event_data,
        created_by=created_by,
        created_at=datetime.utcnow()
    )
    db.session.add(event)
    db.session.flush()
    return event


def create_location(user_id, latitude, longitude):
    """Create a location and return the instance."""
    location = Location(
        id=str(uuid.uuid4()),
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        accuracy=uniform(5, 20),
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.session.add(location)
    db.session.flush()
    return location


def create_notification(user_id, title, message, notification_type, reference_id):
    """Create a notification and return the instance."""
    notification = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_id=reference_id,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.session.add(notification)
    db.session.flush()
    return notification 