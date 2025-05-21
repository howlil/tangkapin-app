# app/routes/notification_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response
from app.models import User, Notification
from app import db

notification_bp = Blueprint('notifications', __name__)

@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications"""
    try:
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        
        notifications_data = [notification.to_dict() for notification in notifications]
        
        return success_response(
            message="Notifications retrieved successfully",
            data={"notifications": notifications_data}
        )
    except Exception as e:
        return error_response(str(e), 500)

@notification_bp.route('/mark-read/<notification_id>', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark notification as read"""
    try:
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        
        if not notification:
            return error_response("Notification not found", 404)
        
        notification.is_read = True
        db.session.commit()
        
        return success_response(
            message="Notification marked as read",
            data={"notification": notification.to_dict()}
        )
    except Exception as e:
        return error_response(str(e), 500)

@notification_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_read():
    """Mark all notifications as read"""
    try:
        user_id = get_jwt_identity()
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        
        return success_response(
            message="All notifications marked as read",
            data={}
        )
    except Exception as e:
        return error_response(str(e), 500) 