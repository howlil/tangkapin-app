from app.models import Camera, User, db
from app.utils.logger import logger
from datetime import datetime

class CameraController:
    @staticmethod
    def get_all_cameras(user_id=None, active_only=True):
        """Get all cameras, optionally filtered by owner"""
        try:
            query = Camera.query
            
            if user_id:
                query = query.filter_by(owner_id=user_id)
                
            if active_only:
                query = query.filter_by(is_active=True)
                
            cameras = query.all()
            return {'cameras': [c.to_dict() for c in cameras]}, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting cameras: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_camera_by_id(camera_id):
        """Get a specific camera by ID"""
        try:
            camera = Camera.query.get(camera_id)
            
            if not camera:
                return {'error': 'Kamera tidak ditemukan'}, 404
                
            return {'camera': camera.to_dict()}, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting camera {camera_id}: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def create_camera(data, owner_id):
        """Create a new camera"""
        try:
            # Validasi data
            required_fields = ['name', 'location', 'stream_url']
            for field in required_fields:
                if not data.get(field):
                    return {'error': f'{field} diperlukan'}, 400
            
            # Create camera object
            camera = Camera(
                name=data['name'],
                description=data.get('description'),
                location=data['location'],
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                stream_url=data['stream_url'],
                cctv_ip=data.get('cctv_ip'),
                status='offline',
                owner_id=owner_id
            )
            
            db.session.add(camera)
            db.session.commit()
            
            logger.logger.info(f"New camera created: {camera.name} (ID: {camera.id})")
            
            return {'message': 'Kamera berhasil ditambahkan', 'camera': camera.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error creating camera: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def update_camera(camera_id, data, user_id):
        """Update a camera"""
        try:
            camera = Camera.query.get(camera_id)
            
            if not camera:
                return {'error': 'Kamera tidak ditemukan'}, 404
            
            # Check ownership
            if camera.owner_id != user_id:
                logger.logger.warning(f"User {user_id} attempted to update camera {camera_id} owned by {camera.owner_id}")
                return {'error': 'Anda tidak memiliki izin untuk mengupdate kamera ini'}, 403
            
            # Update fields
            updatable_fields = ['name', 'description', 'location', 'latitude', 'longitude', 
                               'stream_url', 'cctv_ip', 'is_active']
            
            for field in updatable_fields:
                if field in data:
                    setattr(camera, field, data[field])
            
            camera.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.logger.info(f"Camera updated: {camera.name} (ID: {camera.id})")
            
            return {'message': 'Kamera berhasil diupdate', 'camera': camera.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error updating camera {camera_id}: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def delete_camera(camera_id, user_id):
        """Delete a camera"""
        try:
            camera = Camera.query.get(camera_id)
            
            if not camera:
                return {'error': 'Kamera tidak ditemukan'}, 404
            
            # Check ownership
            if camera.owner_id != user_id:
                logger.logger.warning(f"User {user_id} attempted to delete camera {camera_id} owned by {camera.owner_id}")
                return {'error': 'Anda tidak memiliki izin untuk menghapus kamera ini'}, 403
            
            db.session.delete(camera)
            db.session.commit()
            
            logger.logger.info(f"Camera deleted: {camera.name} (ID: {camera.id})")
            
            return {'message': 'Kamera berhasil dihapus'}, 200
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error deleting camera {camera_id}: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def update_camera_status(camera_id, status, user_id=None):
        """Update camera status"""
        try:
            camera = Camera.query.get(camera_id)
            
            if not camera:
                return {'error': 'Kamera tidak ditemukan'}, 404
            
            # Check ownership if user_id provided
            if user_id and camera.owner_id != user_id:
                logger.logger.warning(f"User {user_id} attempted to update status of camera {camera_id} owned by {camera.owner_id}")
                return {'error': 'Anda tidak memiliki izin untuk mengupdate status kamera ini'}, 403
            
            camera.status = status
            
            # If going online, update the last_online timestamp
            if status == 'online':
                camera.last_online = datetime.utcnow()
                
            db.session.commit()
            
            logger.logger.info(f"Camera status updated: {camera.name} (ID: {camera.id}) - Status: {status}")
            
            return {'message': f'Status kamera berhasil diupdate menjadi {status}', 'camera': camera.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error updating camera status {camera_id}: {e}")
            return {'error': str(e)}, 500 