from app.models import User, db
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app.utils.logger import logger

class AuthController:
    @staticmethod
    def login(email, password):
        """Handle user login logic"""
        try:
            # Validasi input
            if not email or not password:
                return {'error': 'Email dan password diperlukan'}, 400
            
            user = User.query.filter_by(email=email, is_active=True).first()
            
            if user and user.check_password(password):
                # Buat access token dengan expiry 24 jam
                access_token = create_access_token(
                    identity=user.id,
                    expires_delta=timedelta(hours=24),
                    additional_claims={
                        'role': user.role.value,
                        'email': user.email
                    }
                )
                
                # Update last login time
                user.last_login = db.func.now()
                db.session.commit()
                
                return {
                    'message': 'Login berhasil',
                    'access_token': access_token,
                    'user': user.to_dict()
                }, 200
            else:
                return {'error': 'Email atau password salah'}, 401
                
        except Exception as e:
            logger.logger.error(f"Login error: {e}")
            return {'error': str(e)}, 500

    @staticmethod
    def register(data):
        """Handle user registration logic"""
        try:
            # Validasi input
            required_fields = ['email', 'password', 'name', 'role']
            for field in required_fields:
                if not data.get(field):
                    return {'error': f'{field} diperlukan'}, 400
            
            # Cek email sudah ada
            if User.query.filter_by(email=data['email']).first():
                return {'error': 'Email sudah terdaftar'}, 400
            
            # Buat user baru
            user = User(
                email=data['email'],
                name=data['name'],
                phone=data.get('phone'),
                role=data['role'],
                badge_number=data.get('badge_number')
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            logger.logger.info(f"New user registered: {user.email}")
            
            return {
                'message': 'Registrasi berhasil',
                'user': user.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Registration error: {e}")
            return {'error': str(e)}, 500

    @staticmethod
    def get_profile(user_id):
        """Get user profile by ID"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return {'error': 'User tidak ditemukan'}, 404
            
            return {
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            logger.logger.error(f"Get profile error: {e}")
            return {'error': str(e)}, 500
            
    @staticmethod
    def update_profile(user_id, data):
        """Update user profile"""
        try:
            user = User.query.get(user_id)
            
            if not user:
                return {'error': 'User tidak ditemukan'}, 404
            
            # Update fields
            updatable_fields = ['name', 'phone', 'address', 'badge_number']
            for field in updatable_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            # Update password if provided
            if data.get('password'):
                user.set_password(data['password'])
                
            db.session.commit()
            
            logger.logger.info(f"Profile updated for user: {user.email}")
            
            return {
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Update profile error: {e}")
            return {'error': str(e)}, 500 