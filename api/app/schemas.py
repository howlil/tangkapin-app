from marshmallow import Schema, fields, validate, validates, ValidationError
from app import ma
from app.models import User, Camera, Report, Evidence, TimelineEvent, Assignment, Location, Notification

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password_hash',)
        load_instance = True
    
    email = fields.Email(required=True)
    name = fields.String(required=True)
    role = fields.String(required=True, validate=validate.OneOf(['admin', 'officer', 'owner']))
    phone = fields.String()
    address = fields.String()
    badge_number = fields.String()
    last_login = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('role')
    def validate_role(self, value):
        if value not in ['admin', 'officer', 'owner']:
            raise ValidationError(f"Role must be one of: admin, officer, owner")


class CameraSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Camera
        load_instance = True
    
    name = fields.String(required=True)
    location = fields.String(required=True)
    stream_url = fields.String(required=True)
    description = fields.String()
    latitude = fields.Float()
    longitude = fields.Float()
    status = fields.String(validate=validate.OneOf(['online', 'offline', 'maintenance']))
    last_online = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class EvidenceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Evidence
        load_instance = True
    
    file_url = fields.String(required=True)
    file_type = fields.String(required=True, validate=validate.OneOf(['image', 'video', 'audio', 'document']))
    description = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TimelineEventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TimelineEvent
        load_instance = True
    
    event_type = fields.String(required=True)
    event_data = fields.Dict(required=True)
    created_at = fields.DateTime(dump_only=True)


class AssignmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Assignment
        load_instance = True
    
    status = fields.String(validate=validate.OneOf(['PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'REJECTED']))
    notes = fields.String()
    response_time = fields.Integer()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Include the related user information
    officer = fields.Nested(lambda: UserSchema(only=('id', 'name', 'badge_number')), dump_only=True)


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        load_instance = True
    
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    accuracy = fields.Float()
    created_at = fields.DateTime(dump_only=True)


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True
    
    title = fields.String(required=True)
    message = fields.String(required=True)
    notification_type = fields.String(required=True)
    is_read = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)


class ReportSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Report
        load_instance = True
    
    title = fields.String(required=True)
    description = fields.String()
    status = fields.String(validate=validate.OneOf(['NEW', 'VERIFIED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'FALSE_ALARM']))
    priority = fields.String(validate=validate.OneOf(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']))
    detection_confidence = fields.Float()
    weapon_type = fields.String()
    detection_image_url = fields.String()
    is_automatic = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Include related objects
    camera = fields.Nested(lambda: CameraSchema(only=('id', 'name', 'location')), dump_only=True)
    reporter = fields.Nested(lambda: UserSchema(only=('id', 'name', 'role')), dump_only=True)
    evidences = fields.List(fields.Nested(EvidenceSchema), dump_only=True)
    timeline_events = fields.List(fields.Nested(TimelineEventSchema), dump_only=True)
    assignments = fields.List(fields.Nested(AssignmentSchema), dump_only=True)


# Registration and login schemas
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    name = fields.String(required=True)
    role = fields.String(required=True, validate=validate.OneOf(['admin', 'officer', 'owner']))
    phone = fields.String()
    address = fields.String()
    badge_number = fields.String()


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class PasswordChangeSchema(Schema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8))


# Detection schema for ML
class DetectionSchema(Schema):
    image = fields.String(required=True)  # Base64 encoded image
    camera_id = fields.String(required=True)
    confidence = fields.Float(required=True)
    weapon_type = fields.String(required=True)
    detection_data = fields.Dict() 