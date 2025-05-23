from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Initialize logger
    from app.utils.logger import logger
    logger.init_app(app)
    
    # Import models
    from app import models
    
    # Register middleware
    from app.middleware import register_middleware
    register_middleware(app)
    
    # Register routes
    from app.routes import register_routes
    register_routes(app)
    
    @app.route('/')
    def index():
        return {'message': 'TangkapIn API Server Running', 'status': 'OK'}
    
    @app.route('/api')
    def api_info():
        return {
            'service': 'TangkapIn Security API',
            'version': '1.0.0',
            'features': {
                'ml_detection': True,
                'real_time_notifications': True,
                'multi_camera_support': True,
                'role_based_access': True
            },
            'endpoints': {
                'auth': '/api/auth',
                'cameras': '/api/cameras',
                'reports': '/api/reports',
                'assignments': '/api/assignments',
                'system': '/api/system'
            }
        }
    
    # Initialize background tasks - updated for Flask 2.0+
    with app.app_context():
        # Note: in production, use a proper task queue like Celery
        # This is just a simple implementation for demonstration
        try:
            from app.services.background_tasks import BackgroundTaskManager
            
            app.logger.info('Initializing background task manager')
            task_manager = BackgroundTaskManager(app)
            task_manager.start_background_tasks()
            
            # Store task manager in app for access
            app.task_manager = task_manager
            app.logger.info('Background tasks started successfully')
        except ImportError as e:
            app.logger.warning(f"Background tasks not initialized: {e}")
    
    app.logger.info('Application initialization complete')
    return app