from flask import current_app
from app import db
from app.models import Report, Camera, User, Evidence, TimelineEvent, Assignment
from app.utils.error_handlers import ApiError
from app.utils.validators import validate_pagination_params, validate_uuid
import uuid
from datetime import datetime

def get_reports(user_id=None, camera_id=None, status=None, page=None, per_page=None, 
               priority=None, sort_by='created_at', sort_order='desc', active_only=True):
    """Get a paginated list of reports.
    
    Args:
        user_id: Filter by reporter/owner ID
        camera_id: Filter by camera ID
        status: Filter by status
        page: Page number
        per_page: Number of items per page
        priority: Filter by priority
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        active_only: Only return active reports
    
    Returns:
        Tuple of (reports, total, page, per_page)
    """
    try:
        # Validate pagination parameters
        page, per_page = validate_pagination_params(page, per_page)
        
        # Build query
        query = Report.query
        
        # Apply filters
        if user_id:
            query = query.filter(Report.reporter_id == user_id)
        
        if camera_id:
            query = query.filter(Report.camera_id == camera_id)
        
        if status:
            query = query.filter(Report.status == status)
        
        if priority:
            query = query.filter(Report.priority == priority)
        
        if active_only:
            query = query.filter(Report.is_active == True)
        
        # Apply sorting
        sort_field = getattr(Report, sort_by, Report.created_at)
        if sort_order == 'asc':
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        reports = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return reports.items, total, page, per_page
    
    except Exception as e:
        current_app.logger.error(f"Error getting reports: {str(e)}")
        raise ApiError('Error retrieving reports', 500)

def get_report_by_id(report_id, user_id=None):
    """Get a report by ID.
    
    Args:
        report_id: The report ID
        user_id: Optional user ID to validate access
        
    Returns:
        Report instance
        
    Raises:
        ApiError: If report not found or not accessible
    """
    if not validate_uuid(report_id):
        raise ApiError('Invalid report ID format', 400)
    
    report = Report.query.get(report_id)
    
    if not report:
        raise ApiError('Report not found', 404)
    
    # Check access rights for non-admin/non-officer users
    if user_id and user_id != report.reporter_id:
        # Check if the user is the camera owner
        camera = Camera.query.get(report.camera_id)
        if not camera or camera.owner_id != user_id:
            # Check if user is an assigned officer
            assignments = Assignment.query.filter_by(report_id=report_id, officer_id=user_id).first()
            if not assignments:
                raise ApiError('You do not have access to this report', 403)
    
    return report

def create_report(data, reporter_id):
    """Create a new report.
    
    Args:
        data: Dictionary containing report data
        reporter_id: User ID of the reporter
        
    Returns:
        Created Report instance
        
    Raises:
        ApiError: If creation fails
    """
    try:
        # Verify reporter exists
        reporter = User.query.get(reporter_id)
        if not reporter:
            raise ApiError('Reporter not found', 404)
        
        # Verify camera exists
        camera = Camera.query.get(data['camera_id'])
        if not camera:
            raise ApiError('Camera not found', 404)
        
        # Set defaults for optional fields
        status = data.get('status', 'NEW')
        priority = data.get('priority', 'MEDIUM')
        is_automatic = data.get('is_automatic', False)
        
        # Create new report
        new_report = Report(
            id=str(uuid.uuid4()),
            title=data['title'],
            description=data.get('description'),
            camera_id=data['camera_id'],
            reporter_id=reporter_id,
            status=status,
            priority=priority,
            detection_confidence=data.get('detection_confidence'),
            weapon_type=data.get('weapon_type'),
            detection_image_url=data.get('detection_image_url'),
            is_automatic=is_automatic,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(new_report)
        
        # Create timeline event for report creation
        timeline_event = TimelineEvent(
            id=str(uuid.uuid4()),
            report_id=new_report.id,
            event_type='status_change',
            event_data={
                'old_status': None,
                'new_status': status,
                'created_by': reporter_id
            },
            created_by=reporter_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(timeline_event)
        db.session.commit()
        
        return new_report
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating report: {str(e)}")
        if 'ApiError' in str(type(e)):
            raise e
        raise ApiError('Error creating report', 500)

def update_report_status(report, new_status, user_id):
    """Update a report's status.
    
    Args:
        report: Report instance
        new_status: New status
        user_id: User ID making the update
        
    Returns:
        Updated Report instance
        
    Raises:
        ApiError: If update fails
    """
    valid_statuses = ['NEW', 'VERIFIED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FALSE_ALARM']
    if new_status not in valid_statuses:
        raise ApiError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}', 400)
    
    try:
        old_status = report.status
        report.status = new_status
        report.updated_at = datetime.utcnow()
        
        # Create timeline event for status change
        timeline_event = TimelineEvent(
            id=str(uuid.uuid4()),
            report_id=report.id,
            event_type='status_change',
            event_data={
                'old_status': old_status,
                'new_status': new_status,
                'created_by': user_id
            },
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(timeline_event)
        db.session.commit()
        
        return report
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating report status: {str(e)}")
        raise ApiError('Error updating report status', 500)

def update_report_priority(report, new_priority, user_id):
    """Update a report's priority.
    
    Args:
        report: Report instance
        new_priority: New priority
        user_id: User ID making the update
        
    Returns:
        Updated Report instance
        
    Raises:
        ApiError: If update fails
    """
    valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    if new_priority not in valid_priorities:
        raise ApiError(f'Invalid priority. Must be one of: {", ".join(valid_priorities)}', 400)
    
    try:
        old_priority = report.priority
        report.priority = new_priority
        report.updated_at = datetime.utcnow()
        
        # Create timeline event for priority change
        timeline_event = TimelineEvent(
            id=str(uuid.uuid4()),
            report_id=report.id,
            event_type='priority_change',
            event_data={
                'old_priority': old_priority,
                'new_priority': new_priority,
                'created_by': user_id
            },
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(timeline_event)
        db.session.commit()
        
        return report
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating report priority: {str(e)}")
        raise ApiError('Error updating report priority', 500)

def add_evidence(report, data, user_id):
    """Add evidence to a report.
    
    Args:
        report: Report instance
        data: Dictionary containing evidence data
        user_id: User ID adding the evidence
        
    Returns:
        Created Evidence instance
        
    Raises:
        ApiError: If creation fails
    """
    try:
        # Validate evidence data
        if 'file_url' not in data:
            raise ApiError('Evidence file URL is required', 400)
        
        if 'file_type' not in data:
            raise ApiError('Evidence file type is required', 400)
        
        valid_file_types = ['image', 'video', 'audio', 'document']
        if data['file_type'] not in valid_file_types:
            raise ApiError(f'Invalid file type. Must be one of: {", ".join(valid_file_types)}', 400)
        
        # Create evidence
        evidence = Evidence(
            id=str(uuid.uuid4()),
            report_id=report.id,
            file_url=data['file_url'],
            file_type=data['file_type'],
            description=data.get('description'),
            created_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(evidence)
        
        # Create timeline event for evidence addition
        timeline_event = TimelineEvent(
            id=str(uuid.uuid4()),
            report_id=report.id,
            event_type='evidence_added',
            event_data={
                'evidence_id': evidence.id,
                'file_type': data['file_type'],
                'created_by': user_id
            },
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.session.add(timeline_event)
        
        # Update report timestamp
        report.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return evidence
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding evidence: {str(e)}")
        if 'ApiError' in str(type(e)):
            raise e
        raise ApiError('Error adding evidence', 500)

def get_report_timeline(report_id, user_id=None):
    """Get the timeline events for a report.
    
    Args:
        report_id: The report ID
        user_id: Optional user ID to validate access
        
    Returns:
        List of TimelineEvent instances
        
    Raises:
        ApiError: If retrieval fails
    """
    try:
        # Verify report exists and user has access
        report = get_report_by_id(report_id, user_id)
        
        # Get timeline events
        events = TimelineEvent.query.filter_by(report_id=report_id).order_by(TimelineEvent.created_at.asc()).all()
        
        return events
    
    except Exception as e:
        current_app.logger.error(f"Error getting report timeline: {str(e)}")
        if 'ApiError' in str(type(e)):
            raise e
        raise ApiError('Error retrieving report timeline', 500)

def create_ml_report(data, camera_id):
    """Create a report from ML detection.
    
    Args:
        data: Dictionary containing detection data
        camera_id: Camera ID where detection occurred
        
    Returns:
        Created Report instance
        
    Raises:
        ApiError: If creation fails
    """
    try:
        # Verify camera exists
        camera = Camera.query.get(camera_id)
        if not camera:
            raise ApiError('Camera not found', 404)
        
        # Get camera owner as reporter
        reporter_id = camera.owner_id
        
        # Set confidence threshold for priority
        confidence = data.get('confidence', 0.0)
        priority = 'LOW'
        if confidence >= 0.95:
            priority = 'CRITICAL'
        elif confidence >= 0.85:
            priority = 'HIGH'
        elif confidence >= 0.75:
            priority = 'MEDIUM'
        
        # Create report data
        report_data = {
            'title': f"Weapon Detection: {data.get('weapon_type', 'Unknown')}",
            'description': f"Automatic detection by ML system. Confidence: {confidence:.2f}",
            'camera_id': camera_id,
            'status': 'NEW',
            'priority': priority,
            'detection_confidence': confidence,
            'weapon_type': data.get('weapon_type'),
            'detection_image_url': data.get('image_url'),
            'is_automatic': True
        }
        
        # Create report
        new_report = create_report(report_data, reporter_id)
        
        return new_report
    
    except Exception as e:
        current_app.logger.error(f"Error creating ML report: {str(e)}")
        if 'ApiError' in str(type(e)):
            raise e
        raise ApiError('Error creating ML report', 500) 