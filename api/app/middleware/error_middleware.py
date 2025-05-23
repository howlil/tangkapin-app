from flask import jsonify
from app.utils.logger import logger
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

def error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(400)
    def bad_request(e):
        """Handle bad request errors"""
        logger.logger.warning(f"400 error: {str(e)}")
        return jsonify({
            'error': 'Bad request',
            'message': str(e)
        }), 400
    
    @app.errorhandler(404)
    def not_found(e):
        """Handle not found errors"""
        logger.logger.info(f"404 error: {str(e)}")
        return jsonify({
            'error': 'Resource not found',
            'message': str(e)
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        """Handle method not allowed errors"""
        logger.logger.warning(f"405 error: {str(e)}")
        return jsonify({
            'error': 'Method not allowed',
            'message': str(e)
        }), 405
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle internal server errors"""
        logger.logger.error(f"500 error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle all other HTTP exceptions"""
        logger.logger.warning(f"HTTP exception: {e.code} - {str(e)}")
        return jsonify({
            'error': e.name,
            'message': str(e)
        }), e.code
    
    @app.errorhandler(SQLAlchemyError)
    def handle_db_exception(e):
        """Handle database errors"""
        logger.logger.error(f"Database error: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': 'A database error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle all uncaught exceptions"""
        logger.logger.error(f"Uncaught exception: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    logger.logger.info("Error handlers initialized") 