from flask import request, g
import time
from app.utils.logger import logger

def request_handlers(app):
    """Register request handlers for the application"""
    
    @app.before_request
    def log_request_info():
        """Log request information before processing"""
        g.start_time = time.time()
        
        # Log basic request info
        logger.logger.info(f"Request started: {request.method} {request.path}")
        
        # Log more detailed info for debugging if needed
        if app.debug:
            logger.logger.debug(f"Request headers: {dict(request.headers)}")
            logger.logger.debug(f"Request args: {dict(request.args)}")
    
    @app.after_request
    def log_response_info(response):
        """Log response information after processing"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            logger.logger.info(f"Request completed: {request.method} {request.path} - "
                         f"Status: {response.status_code} - Duration: {duration:.4f}s")
            
            # For longer requests, add a warning log
            if duration > 1.0:  # Adjust threshold as needed
                logger.logger.warning(f"Slow request: {request.method} {request.path} - "
                              f"Duration: {duration:.4f}s")
        
        return response
    
    logger.logger.info("Request handlers initialized") 