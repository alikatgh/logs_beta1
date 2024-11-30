import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Base configuration with common settings"""

    # Environment settings
    ENV = 'development'  # Default to production for safety
    FORCE_HTTPS = False  # Default to True for safety

    # Security settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "generate-a-secure-key-in-production"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = False
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

    # Authentication settings
    LOGIN_VIEW = "auth.login"
    LOGIN_MESSAGE_CATEGORY = "info"

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

    # Cache settings
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300

    # Session settings
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(basedir, "flask_session")

    # API settings
    API_RATE_LIMITING = True
    API_RATE_LIMIT = "100 per minute"

    # Logging settings
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT", "false").lower() == "true"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    @staticmethod
    def init_app(app):
        """Initialize application with config-specific settings"""
        # Ensure upload folder exists
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        # Ensure session folder exists
        os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    # Environment settings
    ENV = 'development'
    DEBUG = True
    DEVELOPMENT = True
    FORCE_HTTPS = False  # Disable HTTPS redirect in development

    # Development database settings
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "instance", "deliveries_dev.db")

    # Override security settings for development
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

    # Email configuration for development
    MAIL_SERVER = "localhost"
    MAIL_PORT = 8025
    MAIL_USE_TLS = False

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        app.logger.info("Development configuration initialized")


class TestingConfig(BaseConfig):
    """Testing configuration"""

    # Environment settings
    ENV = 'testing'
    TESTING = True
    FORCE_HTTPS = False  # Disable HTTPS redirect in testing

    # Testing database settings
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "localhost.localdomain"

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        app.logger.info("Testing configuration initialized")


class ProductionConfig(BaseConfig):
    """Production configuration"""

    # Environment settings
    ENV = 'production'
    DEBUG = False
    TESTING = False
    FORCE_HTTPS = True  # Enable HTTPS redirect in production

    # Production database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "instance", "deliveries.db")

    # Production security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # Production email settings
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        # Log to stdout in production
        if app.config["LOG_TO_STDOUT"]:
            import logging

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(getattr(logging, app.config["LOG_LEVEL"]))
            app.logger.addHandler(stream_handler)

        # Production-specific security headers
        @app.after_request
        def add_security_headers(response):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
            response.headers["Content-Security-Policy"] = "default-src 'self'"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            return response


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
