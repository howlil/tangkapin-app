from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from app.services.report_service import (
    get_reports,
    get_report_by_id,
    create_report,
    update_report_status,
    update_report_priority,
    add_evidence,
    get_report_timeline
)
from app.schemas import ReportSchema, TimelineEventSchema, EvidenceSchema
from app.middleware.auth import admin_required, officer_or_admin_required
from app.utils.validators import validate_json_payload
from app.utils.error_handlers import ApiError

@jwt_required()
def get_all_reports():
    """Get all reports (filtered by role)."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        priority = request.args.get('priority')
        camera_id = request.args.get('camera_id')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        include_inactive = request.args.get('include_inactive', '').lower() in ['true', '1', 'yes']
        
        # Filter by user for non-admin/non-officer users
        user_id = None
        if current_user.role == 'owner':
            user_id = current_user.id
        
        # Get reports
        reports, total, current_page, items_per_page = get_reports(
            user_id=user_id,
            camera_id=camera_id,
            status=status,
            page=page,
            per_page=per_page,
            priority=priority,
            sort_by=sort_by,
            sort_order=sort_order,
            active_only=not include_inactive
        )
        
        # Serialize reports
        report_schema = ReportSchema(many=True)
        reports_data = report_schema.dump(reports)
        
        return jsonify({
            'reports': reports_data,
            'pagination': {
                'total': total,
                'page': current_page,
                'per_page': items_per_page,
                'pages': (total // items_per_page) + (1 if total % items_per_page > 0 else 0)
            }
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def get_report(report_id):
    """Get a report by ID."""
    try:
        # Get report (automatically checks access rights for non-admin users)
        user_id = None if current_user.role in ['admin', 'officer'] else current_user.id
        report = get_report_by_id(report_id, user_id)
        
        return jsonify(ReportSchema().dump(report)), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def create_new_report():
    """Create a new report."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['title', 'camera_id'])
    if validation_error:
        return validation_error
    
    try:
        # Create report
        new_report = create_report(data, current_user.id)
        
        return jsonify({
            'message': 'Report created successfully',
            'report': ReportSchema().dump(new_report)
        }), 201
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
@officer_or_admin_required()
def update_report_status_endpoint(report_id):
    """Update a report's status."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['status'])
    if validation_error:
        return validation_error
    
    try:
        # Get report
        report = get_report_by_id(report_id)
        
        # Update status
        updated_report = update_report_status(report, data['status'], current_user.id)
        
        return jsonify({
            'message': f"Report status updated to '{data['status']}'",
            'report': ReportSchema().dump(updated_report)
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
@officer_or_admin_required()
def update_report_priority_endpoint(report_id):
    """Update a report's priority."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['priority'])
    if validation_error:
        return validation_error
    
    try:
        # Get report
        report = get_report_by_id(report_id)
        
        # Update priority
        updated_report = update_report_priority(report, data['priority'], current_user.id)
        
        return jsonify({
            'message': f"Report priority updated to '{data['priority']}'",
            'report': ReportSchema().dump(updated_report)
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def add_evidence_endpoint(report_id):
    """Add evidence to a report."""
    data = request.get_json()
    
    # Validate JSON payload
    validation_error = validate_json_payload(data, ['file_url', 'file_type'])
    if validation_error:
        return validation_error
    
    try:
        # Get report (automatically checks access rights for non-admin users)
        user_id = None if current_user.role in ['admin', 'officer'] else current_user.id
        report = get_report_by_id(report_id, user_id)
        
        # Add evidence
        evidence = add_evidence(report, data, current_user.id)
        
        return jsonify({
            'message': 'Evidence added successfully',
            'evidence': EvidenceSchema().dump(evidence)
        }), 201
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code

@jwt_required()
def get_report_timeline_endpoint(report_id):
    """Get the timeline for a report."""
    try:
        # Get report timeline (automatically checks access rights)
        user_id = None if current_user.role in ['admin', 'officer'] else current_user.id
        events = get_report_timeline(report_id, user_id)
        
        # Serialize events
        timeline_schema = TimelineEventSchema(many=True)
        events_data = timeline_schema.dump(events)
        
        return jsonify({
            'report_id': report_id,
            'timeline': events_data
        }), 200
    
    except ApiError as e:
        return jsonify({'error': e.message, 'details': e.details}), e.status_code 