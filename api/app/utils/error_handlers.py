from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.exceptions import HTTPException
import json

class ErrorResponse:
    def __init__(self, message, status_code, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
    
    def to_dict(self):
        response = {
            'error': self.message,
            'status_code': self.status_code
        }
        if self.details:
            response['details'] = self.details
        return response


class ApiError(Exception):
    def __init__(self, message, status_code=400, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify(ErrorResponse(
            message="Validation error",
            status_code=400,
            details=e.messages
        ).to_dict()), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        return jsonify(ErrorResponse(
            message="Database integrity error",
            status_code=400,
            details=str(e.orig)
        ).to_dict()), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e):
        return jsonify(ErrorResponse(
            message="Database error",
            status_code=500,
            details=str(e)
        ).to_dict()), 500
    
    @app.errorhandler(ApiError)
    def handle_api_error(e):
        return jsonify(ErrorResponse(
            message=e.message,
            status_code=e.status_code,
            details=e.details
        ).to_dict()), e.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify(ErrorResponse(
            message=e.description,
            status_code=e.code
        ).to_dict()), e.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        return jsonify(ErrorResponse(
            message="Internal server error",
            status_code=500,
            details=str(e) if app.config.get('DEBUG', False) else None
        ).to_dict()), 500
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify(ErrorResponse(
            message="Resource not found",
            status_code=404
        ).to_dict()), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify(ErrorResponse(
            message="Method not allowed",
            status_code=405
        ).to_dict()), 405 