from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.assignment_controller import AssignmentController
from app.middleware.auth_middleware import admin_required, officer_required
from app.models import Assignment, Location, db
from app.utils.logger import logger

# Create blueprint
assignments_bp = Blueprint('assignments', __name__)

@assignments_bp.route('', methods=['GET'])
@jwt_required()
def get_assignments():
    """Get all assignments"""
    user_id = get_jwt_identity()
    status = request.args.get('status')
    
    response, status_code = AssignmentController.get_all_assignments(user_id, status)
    return jsonify(response), status_code

@assignments_bp.route('/<assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment(assignment_id):
    """Get assignment by ID"""
    response, status_code = AssignmentController.get_assignment_by_id(assignment_id)
    return jsonify(response), status_code

@assignments_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_assignment():
    """Create a new assignment (admin only)"""
    admin_id = get_jwt_identity()
    data = request.get_json()
    
    response, status_code = AssignmentController.create_assignment(data, admin_id)
    return jsonify(response), status_code

@assignments_bp.route('/<assignment_id>', methods=['PUT'])
@jwt_required()
def update_assignment(assignment_id):
    """Update assignment"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    response, status_code = AssignmentController.update_assignment(assignment_id, data, user_id)
    return jsonify(response), status_code

@assignments_bp.route('/<assignment_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_assignment(assignment_id):
    """Delete assignment (admin only)"""
    admin_id = get_jwt_identity()
    
    response, status_code = AssignmentController.delete_assignment(assignment_id, admin_id)
    return jsonify(response), status_code

@assignments_bp.route('/<assignment_id>/location', methods=['POST'])
@jwt_required()
@officer_required
def update_officer_location(assignment_id):
    """Update officer location for assignment"""
    officer_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Validasi data
        required_fields = ['latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Field {field} diperlukan'}), 400
        
        # Verifikasi penugasan
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'error': 'Penugasan tidak ditemukan'}), 404
            
        if assignment.officer_id != officer_id:
            logger.logger.warning(f"Officer {officer_id} attempted to update location for assignment {assignment_id} assigned to {assignment.officer_id}")
            return jsonify({'error': 'Anda tidak memiliki akses ke penugasan ini'}), 403
        
        # Update lokasi terakhir petugas
        location = Location(
            user_id=officer_id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy', 10),
            is_active=True,
            assignment_id=assignment_id
        )
        
        db.session.add(location)
        db.session.commit()
        
        logger.logger.info(f"Officer {officer_id} location updated for assignment {assignment_id}")
        
        return jsonify({
            'message': 'Lokasi berhasil diperbarui',
            'location': {
                'id': location.id,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'accuracy': location.accuracy,
                'timestamp': location.created_at.isoformat() if location.created_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.logger.error(f"Error updating location: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/<assignment_id>/locations', methods=['GET'])
@jwt_required()
def get_assignment_locations(assignment_id):
    """Get location history for assignment"""
    user_id = get_jwt_identity()
    
    try:
        # Verifikasi penugasan
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'error': 'Penugasan tidak ditemukan'}), 404
            
        # Hanya admin, petugas yang ditugaskan, atau yang membuat penugasan yang boleh melihat
        is_admin = assignment.assigned_by == user_id
        is_assigned_officer = assignment.officer_id == user_id
        
        if not (is_admin or is_assigned_officer):
            logger.logger.warning(f"User {user_id} attempted to access location history for assignment {assignment_id}")
            return jsonify({'error': 'Anda tidak memiliki akses ke data lokasi ini'}), 403
        
        # Ambil riwayat lokasi
        locations = Location.query.filter_by(
            assignment_id=assignment_id
        ).order_by(Location.created_at.desc()).all()
        
        return jsonify({
            'assignment_id': assignment_id,
            'officer_id': assignment.officer_id,
            'locations': [{
                'id': loc.id,
                'latitude': loc.latitude,
                'longitude': loc.longitude,
                'accuracy': loc.accuracy,
                'timestamp': loc.created_at.isoformat() if loc.created_at else None
            } for loc in locations]
        }), 200
        
    except Exception as e:
        logger.logger.error(f"Error getting location history: {str(e)}")
        return jsonify({'error': str(e)}), 500 