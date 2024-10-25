from datetime import datetime
from time import time

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from app import db, login_manager


class User(UserMixin, db.Model):
    """User model for authentication and user management"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_password_change = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
        self.last_password_change = datetime.utcnow()

    def check_password(self, password):
        """Verify the user's password"""
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        """
        Generate a password reset token

        Args:
            expires_in (int): Token expiration time in seconds (default: 10 minutes)

        Returns:
            str: JWT token for password reset
        """
        return jwt.encode(
            {
                "reset_password": self.id,
                "exp": time() + expires_in,
                "iat": time(),  # Include issued at time
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        """
        Verify a password reset token

        Args:
            token (str): JWT token to verify

        Returns:
            User|None: User object if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            user_id = payload["reset_password"]
            return User.query.get(user_id)

        except jwt.ExpiredSignatureError:
            current_app.logger.warning(f"Expired reset token: {token}")
            return None

        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Invalid reset token: {token}, Error: {str(e)}")
            return None

        except Exception as e:
            current_app.logger.error(f"Unexpected error verifying token: {str(e)}")
            return None

    def is_token_expired(self, token):
        """Check if a token is expired without raising an exception"""
        try:
            jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            return False
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return True

    def get_token_expiry(self, token):
        """Get the expiration time of a token"""
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            return datetime.fromtimestamp(payload["exp"])
        except (jwt.InvalidTokenError, KeyError):
            return None

    @property
    def is_password_expired(self):
        """Check if user's password has expired"""
        if not self.last_password_change:
            return True

        password_max_age = current_app.config.get(
            "PASSWORD_MAX_AGE", 7776000
        )  # 90 days
        age = (datetime.utcnow() - self.last_password_change).total_seconds()
        return age > password_max_age

    def __repr__(self):
        """String representation of User"""
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(id):
    """Load user by ID for Flask-Login"""
    try:
        return User.query.get(int(id))
    except (ValueError, TypeError) as e:
        current_app.logger.error(f"Error loading user with ID {id}: {str(e)}")
        return None
