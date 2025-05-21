# app/routes/location_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response
from app.models import User, Location
from app import db
from datetime import datetime

location_bp = Blueprint('locations', __name__)

@location_bp.route('/update', methods=['POST'])
@jwt_required()
def update_location():
    """Update user location"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return error_response("Latitude and longitude are required", 400)
        
        user = User.query.get(user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        # Create new location entry
        location = Location(
            user_id=user_id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy'),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(location)
        db.session.commit()
        
        return success_response(
            message="Location updated successfully",
            data={"location": location.to_dict()}
        )
    except Exception as e:
        return error_response(str(e), 500)

@location_bp.route('/officers', methods=['GET'])
@jwt_required()
def get_officer_locations():
    """Get all active officer locations"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role not in ['admin', 'officer']:
            return error_response("Not authorized", 403)
        
        # Get the most recent location for each active officer
        officers = User.query.filter_by(role='officer', is_active=True).all()
        officer_locations = []
        
        for officer in officers:
            latest_location = Location.query.filter_by(
                user_id=officer.id, 
                is_active=True
            ).order_by(Location.created_at.desc()).first()
            
            if latest_location:
                officer_data = officer.to_dict()
                officer_data['location'] = latest_location.to_dict()
                officer_locations.append(officer_data)
        
        return success_response(
            message="Officer locations retrieved successfully",
            data={"officers": officer_locations}
        )
    except Exception as e:
        return error_response(str(e), 500)

@location_bp.route('/history/<user_id>', methods=['GET'])
@jwt_required()
def get_location_history(user_id):
    """Get location history for a user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return error_response("Not authorized", 403)
        
        target_user = User.query.get(user_id)
        
        if not target_user:
            return error_response("User not found", 404)
        
        locations = Location.query.filter_by(
            user_id=user_id
        ).order_by(Location.created_at.desc()).limit(100).all()
        
        location_data = [location.to_dict() for location in locations]
        
        return success_response(
            message="Location history retrieved successfully",
            data={"locations": location_data}
        )
    except Exception as e:
        return error_response(str(e), 500) 