from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.report_controller import ReportController
from app.middleware.auth_middleware import admin_required, officer_required

# Create blueprint
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods=['GET'])
@jwt_required()
def get_reports():
    """Get all reports"""
    user_id = get_jwt_identity()
    status = request.args.get('status')
    
    response, status_code = ReportController.get_all_reports(user_id, status)
    return jsonify(response), status_code

@reports_bp.route('/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get report by ID"""
    response, status_code = ReportController.get_report_by_id(report_id)
    return jsonify(response), status_code

@reports_bp.route('', methods=['POST'])
@jwt_required()
def create_report():
    """Create a new report"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    response, status_code = ReportController.create_report(data, user_id)
    return jsonify(response), status_code

@reports_bp.route('/<report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """Update report"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    response, status_code = ReportController.update_report(report_id, data, user_id)
    return jsonify(response), status_code

@reports_bp.route('/<report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete report"""
    user_id = get_jwt_identity()
    
    response, status_code = ReportController.delete_report(report_id, user_id)
    return jsonify(response), status_code 