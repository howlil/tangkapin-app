# run.py
import os
from app import create_app, db, register_cli_commands
from app.models import User, Camera, Report, Assignment, Location, ReportUpdate, Notification, PerformanceMetric
from dotenv import load_dotenv
from flask import jsonify

# Load environment variables
load_dotenv()

# Create application instance
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)



# Register CLI commands
register_cli_commands(app)

# Add error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "Resource not found",
        "error": 404
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "message": "Bad request",
        "error": 400
    }), 400

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "message": "Internal server error",
        "error": 500
    }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to check if API is working"""
    return jsonify({
        "success": True,
        "message": "API is working correctly",
        "data": {"version": app.config.get('APP_VERSION', '1.0.0')}
    })

@app.shell_context_processor
def make_shell_context():
    """Make database models available in shell context"""
    return {
        'db': db,
        'User': User,
        'Camera': Camera,
        'Report': Report,
        'Assignment': Assignment,
        'Location': Location,
        'ReportUpdate': ReportUpdate,
        'Notification': Notification,
        'PerformanceMetric': PerformanceMetric
    }

# Only execute when running directly, not when imported
if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('HOST', '127.0.0.1')  # Changed from 0.0.0.0 to 127.0.0.1
    port = int(os.getenv('PORT', 8080))    # Changed default port from 5000 to 8080
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # Create tables if they don't exist
    with app.app_context():
        # Check if we need to run database migrations
        if db.engine.url.drivername == 'postgresql':
            # SQLite doesn't support ALTER fully, use create_all for simplicity
            db.create_all()
        else:
            try:
                # Run migrations
                from flask_migrate import upgrade, init
                
                if not os.path.exists('migrations'):
                    # Initialize migrations if not exists
                    init()
                
                upgrade()
            except Exception as e:
                app.logger.warning(f"Migration error: {e}")
                # Create tables manually if migrations fail
                db.create_all()
    
    # Disable werkzeug's reloader in production to prevent issues with multiple processes
    use_reloader = True if debug else False
    
    # Start the development server
    app.run(host=host, port=port, debug=debug, use_reloader=use_reloader, threaded=True)