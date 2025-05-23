from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.system_controller import SystemController
from app.middleware.auth_middleware import admin_required

# Create blueprint
system_bp = Blueprint('system', __name__)

@system_bp.route('/status', methods=['GET'])
@jwt_required()
def get_system_status():
    """Get system status"""
    response, status_code = SystemController.get_system_status()
    return jsonify(response), status_code

@system_bp.route('/metrics', methods=['GET'])
@jwt_required()
@admin_required
def get_system_metrics():
    """Get system metrics (admin only)"""
    response, status_code = SystemController.get_system_metrics()
    return jsonify(response), status_code

@system_bp.route('/backup', methods=['POST'])
@jwt_required()
@admin_required
def create_backup():
    """Create system backup (admin only)"""
    response, status_code = SystemController.create_backup()
    return jsonify(response), status_code

@system_bp.route('/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_system_logs():
    """Get system logs (admin only)"""
    lines = request.args.get('lines', 100, type=int)
    response, status_code = SystemController.get_logs(lines)
    return jsonify(response), status_code

@system_bp.route('/test-notification', methods=['POST'])
@jwt_required()
@admin_required
def send_test_notification():
    """Send test notification (admin only)"""
    user_id = get_jwt_identity()
    response, status_code = SystemController.send_test_notification(user_id)
    return jsonify(response), status_code 