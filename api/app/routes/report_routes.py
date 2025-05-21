from flask import Blueprint
from app.controllers.reports import (
    get_all_reports,
    get_report,
    create_new_report,
    update_report_status_endpoint,
    update_report_priority_endpoint,
    add_evidence_endpoint,
    get_report_timeline_endpoint
)

report_bp = Blueprint('reports', __name__)

# Get all reports (filtered by role)
@report_bp.route('', methods=['GET'])
def get_reports_route():
    """Get all reports (filtered by role)."""
    return get_all_reports()

# Get a specific report
@report_bp.route('/<report_id>', methods=['GET'])
def get_report_route(report_id):
    """Get a report by ID."""
    return get_report(report_id)

# Create a new report
@report_bp.route('', methods=['POST'])
def create_report_route():
    """Create a new report."""
    return create_new_report()

# Update report status
@report_bp.route('/<report_id>/status', methods=['PUT'])
def update_status_route(report_id):
    """Update a report's status."""
    return update_report_status_endpoint(report_id)

# Update report priority
@report_bp.route('/<report_id>/priority', methods=['PUT'])
def update_priority_route(report_id):
    """Update a report's priority."""
    return update_report_priority_endpoint(report_id)

# Add evidence to a report
@report_bp.route('/<report_id>/evidence', methods=['POST'])
def add_evidence_route(report_id):
    """Add evidence to a report."""
    return add_evidence_endpoint(report_id)

# Get report timeline
@report_bp.route('/<report_id>/timeline', methods=['GET'])
def get_timeline_route(report_id):
    """Get the timeline for a report."""
    return get_report_timeline_endpoint(report_id) 