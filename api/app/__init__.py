# app/__init__.py
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
import logging
from logging.handlers import RotatingFileHandler
import os
import bleach

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
talisman = Talisman()

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Setup CORS - updated configuration for development
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    
    # Disable CSP for development
    if config_name == 'development':
        talisman.init_app(app, content_security_policy=None, force_https=False)
    else:
        talisman.init_app(app)
    
    # Setup caching
    cache_config = {
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple'),
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    if app.config.get('REDIS_URL'):
        cache_config['CACHE_REDIS_URL'] = app.config.get('REDIS_URL')
    
    cache.init_app(app, config=cache_config)
    
    # Import models to ensure they're registered
    from app.models import (User, Camera, Report, Assignment, Location, 
                           ReportUpdate, Notification, PerformanceMetric)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.camera_routes import camera_bp
    from app.routes.report_routes import report_bp
    from app.routes.ml_routes import ml_bp
    from app.routes.notification_routes import notification_bp
    from app.routes.assignment_routes import assignment_bp
    from app.routes.location_routes import location_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(camera_bp, url_prefix='/api/cameras')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(assignment_bp, url_prefix='/api/assignments')
    app.register_blueprint(location_bp, url_prefix='/api/locations')
    
    # Add OPTIONS response for all routes
    add_options_to_all_routes(app)
    
    # Register additional routes
    register_additional_routes(app)
    
    # Setup error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)
    
    # Create upload directories
    setup_upload_directories(app)
    
    # Setup CLI commands
    from app.utils.cli import register_cli_commands
    register_cli_commands(app)
    
    return app

def add_options_to_all_routes(app):
    """Add OPTIONS method handler to all routes to support CORS preflight requests"""
    from flask import make_response, jsonify, request
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path):
        return make_response(jsonify({"status": "ok"}), 200)

def register_additional_routes(app):
    """Register additional routes not in blueprints"""
    
    @app.route('/')
    def index():
        """API root endpoint"""
        return jsonify({
            "error": False,
            "message": f"Welcome to {app.config['APP_NAME']} API",
            "data": {
                "version": app.config['APP_VERSION'],
                "api_version": app.config['API_VERSION'],
                "endpoints": {
                    "auth": "/api/v1/auth",
                    "dashboard": "/api/v1/dashboard",
                    "cameras": "/api/v1/cameras",
                    "officers": "/api/v1/officers",
                    "reports": "/api/v1/reports",
                    "notifications": "/api/v1/notifications",
                    "analytics": "/api/v1/analytics"
                }
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        return jsonify({
            "error": False,
            "message": "Health check completed",
            "data": {
                "status": "healthy" if db_status == "healthy" else "unhealthy",
                "database": db_status,
                "timestamp": db.func.now()
            }
        })
    
    @app.route('/api/v1/status')
    def api_status():
        """API status endpoint"""
        return jsonify({
            "error": False,
            "message": "Status retrieved successfully",
            "data": {
                "api_name": app.config['APP_NAME'],
                "version": app.config['APP_VERSION'],
                "environment": app.config['FLASK_ENV'],
                "debug": app.config['DEBUG'],
                "status": "running"
            }
        })

def setup_logging(app):
    """Setup application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.dirname(app.config['LOG_FILE'])
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        # Set log level
        log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(log_level)
        app.logger.info(f'{app.config["APP_NAME"]} startup')

def setup_upload_directories(app):
    """Create upload directories if they don't exist"""
    upload_dirs = [
        app.config['UPLOAD_FOLDER'],
        os.path.join(app.config['UPLOAD_FOLDER'], 'evidence'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'reports'),
        'temp_detections'
    ]
    
    for directory in upload_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            app.logger.info(f'Created directory: {directory}')

# Create utility function for sanitizing inputs
def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if text is None:
        return None
    return bleach.clean(text, strip=True)

# CLI commands for managing the application
def register_cli_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        db.create_all()
        print('Database initialized!')
    
    @app.cli.command()
    def drop_db():
        """Drop all database tables"""
        db.drop_all()
        print('Database dropped!')
    
    @app.cli.command()
    def seed_db():
        """Seed the database with initial data"""
        from app.utils.seeders import seed_initial_data
        seed_initial_data()
        print('Database seeded!')
    
    @app.cli.command()
    def create_admin():
        """Create admin user"""
        from app.models import User, UserRole
        import getpass
        
        email = input('Admin email: ')
        name = input('Admin name: ')
        password = getpass.getpass('Admin password: ')
        
        admin = User(
            email=email,
            name=name,
            role=UserRole.ADMIN
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f'Admin user {email} created successfully!')