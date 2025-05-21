from flask import current_app
from app import db
from app.models import Camera, User
from app.utils.error_handlers import ApiError
from app.utils.validators import validate_pagination_params, validate_uuid
import uuid
from datetime import datetime

def get_cameras(user_id=None, page=None, per_page=None, status=None, active_only=True):
    """Get a paginated list of cameras.
    
    Args:
        user_id: Filter by owner ID
        page: Page number
        per_page: Number of items per page
        status: Filter by status
        active_only: Only return active cameras
    
    Returns:
        Tuple of (cameras, total, page, per_page)
    """
    try:
        # Validate pagination parameters
        page, per_page = validate_pagination_params(page, per_page)
        
        # Build query
        query = Camera.query
        
        # Apply filters
        if user_id:
            query = query.filter(Camera.owner_id == user_id)
        
        if status:
            query = query.filter(Camera.status == status)
        
        if active_only:
            query = query.filter(Camera.is_active == True)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        cameras = query.order_by(Camera.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return cameras.items, total, page, per_page
    
    except Exception as e:
        current_app.logger.error(f"Error getting cameras: {str(e)}")
        raise ApiError('Error retrieving cameras', 500)

def get_camera_by_id(camera_id, user_id=None):
    """Get a camera by ID.
    
    Args:
        camera_id: The camera ID
        user_id: Optional owner ID to validate ownership
        
    Returns:
        Camera instance
        
    Raises:
        ApiError: If camera not found or not owned by user
    """
    if not validate_uuid(camera_id):
        raise ApiError('Invalid camera ID format', 400)
    
    camera = Camera.query.get(camera_id)
    
    if not camera:
        raise ApiError('Camera not found', 404)
    
    if user_id and camera.owner_id != user_id:
        raise ApiError('You do not have access to this camera', 403)
    
    return camera

def create_camera(data, owner_id):
    """Create a new camera.
    
    Args:
        data: Dictionary containing camera data
        owner_id: User ID of the camera owner
        
    Returns:
        Created Camera instance
        
    Raises:
        ApiError: If creation fails
    """
    try:
        # Verify owner exists
        owner = User.query.get(owner_id)
        if not owner:
            raise ApiError('Owner not found', 404)
        
        # Create new camera
        new_camera = Camera(
            id=str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description'),
            location=data['location'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            stream_url=data['stream_url'],
            status=data.get('status', 'offline'),
            owner_id=owner_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(new_camera)
        db.session.commit()
        
        return new_camera
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating camera: {str(e)}")
        if 'ApiError' in str(type(e)):
            raise e
        raise ApiError('Error creating camera', 500)

def update_camera(camera, data):
    """Update a camera.
    
    Args:
        camera: Camera instance to update
        data: Dictionary containing update data
        
    Returns:
        Updated Camera instance
        
    Raises:
        ApiError: If update fails
    """
    try:
        # Update fields if provided
        if 'name' in data:
            camera.name = data['name']
        
        if 'description' in data:
            camera.description = data['description']
        
        if 'location' in data:
            camera.location = data['location']
        
        if 'latitude' in data:
            camera.latitude = data['latitude']
        
        if 'longitude' in data:
            camera.longitude = data['longitude']
        
        if 'stream_url' in data:
            camera.stream_url = data['stream_url']
        
        if 'status' in data:
            camera.status = data['status']
        
        camera.updated_at = datetime.utcnow()
        db.session.commit()
        
        return camera
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating camera: {str(e)}")
        raise ApiError('Error updating camera', 500)

def update_camera_status(camera, status):
    """Update a camera's status.
    
    Args:
        camera: Camera instance
        status: New status (online, offline, maintenance)
        
    Returns:
        Updated Camera instance
        
    Raises:
        ApiError: If update fails
    """
    valid_statuses = ['online', 'offline', 'maintenance']
    if status not in valid_statuses:
        raise ApiError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}', 400)
    
    try:
        camera.status = status
        
        # Update last_online timestamp if changing to online
        if status == 'online':
            camera.last_online = datetime.utcnow()
        
        camera.updated_at = datetime.utcnow()
        db.session.commit()
        
        return camera
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating camera status: {str(e)}")
        raise ApiError('Error updating camera status', 500)

def delete_camera(camera):
    """Delete a camera.
    
    Args:
        camera: Camera instance
        
    Returns:
        True if successful
        
    Raises:
        ApiError: If deletion fails
    """
    try:
        db.session.delete(camera)
        db.session.commit()
        
        return True
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting camera: {str(e)}")
        raise ApiError('Error deleting camera - may have related records', 500)

def get_secure_stream_url(camera):
    """Generate a secure URL for camera stream access.
    
    Args:
        camera: Camera instance
        
    Returns:
        Secure URL with temporary access token
    """
    try:
        # In a real application, this would generate a signed URL with 
        # limited-time access to the camera stream. For this implementation,
        # we'll just return the original URL.
        
        # Update last access time
        camera.updated_at = datetime.utcnow()
        db.session.commit()
        
        return camera.stream_url
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating secure stream URL: {str(e)}")
        raise ApiError('Error generating secure stream URL', 500) 