"""
Routes module for registering all application routes.
"""

def register_routes(app):
    """Register all application routes with the Flask app"""
    from app.routes.auth_routes import auth_bp
    from app.routes.camera_routes import cameras_bp
    from app.routes.report_routes import reports_bp
    from app.routes.assignment_routes import assignments_bp
    from app.routes.system_routes import system_bp
    from app.routes.multi_camera_routes import multi_camera_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(cameras_bp, url_prefix='/api/cameras')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(assignments_bp, url_prefix='/api/assignments')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(multi_camera_bp, url_prefix='/api/multi-camera')
    
    app.logger.info('All routes registered successfully')