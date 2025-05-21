# app/routes/assignment_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response
from app.models import User, Assignment, Report
from app import db

assignment_bp = Blueprint('assignments', __name__)

@assignment_bp.route('/', methods=['GET'])
@jwt_required()
def get_assignments():
    """Get user assignments"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        if user.role == 'admin':
            # Admins can see all assignments
            assignments = Assignment.query.order_by(Assignment.created_at.desc()).all()
        else:
            # Officers only see their own assignments
            assignments = Assignment.query.filter_by(officer_id=user_id).order_by(Assignment.created_at.desc()).all()
        
        assignments_data = [assignment.to_dict() for assignment in assignments]
        
        return success_response(
            message="Assignments retrieved successfully",
            data={"assignments": assignments_data}
        )
    except Exception as e:
        return error_response(str(e), 500)

@assignment_bp.route('/<assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment(assignment_id):
    """Get assignment details"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        assignment = Assignment.query.get(assignment_id)
        
        if not assignment:
            return error_response("Assignment not found", 404)
        
        # Check permission
        if user.role != 'admin' and assignment.officer_id != user_id:
            return error_response("Not authorized to view this assignment", 403)
        
        return success_response(
            message="Assignment retrieved successfully",
            data={"assignment": assignment.to_dict()}
        )
    except Exception as e:
        return error_response(str(e), 500)

@assignment_bp.route('/update-status/<assignment_id>', methods=['PUT'])
@jwt_required()
def update_assignment_status(assignment_id):
    """Update assignment status"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'status' not in data:
            return error_response("Status is required", 400)
        
        assignment = Assignment.query.get(assignment_id)
        
        if not assignment:
            return error_response("Assignment not found", 404)
        
        # Check permission
        if assignment.officer_id != user_id:
            return error_response("Not authorized to update this assignment", 403)
        
        # Update status
        assignment.status = data['status']
        
        # If the assignment is completed, update the report status
        if data['status'] == 'COMPLETED':
            report = Report.query.get(assignment.report_id)
            if report:
                report.status = 'COMPLETED'
        
        db.session.commit()
        
        return success_response(
            message="Assignment status updated successfully",
            data={"assignment": assignment.to_dict()}
        )
    except Exception as e:
        return error_response(str(e), 500) 