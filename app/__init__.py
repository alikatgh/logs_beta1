import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, current_app, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
# s
from flask_mail import Mail
from flask_babel import Babel
from app.routes import init_app as init_routes

# os.environ['WERKZEUG_SERVER_FD'] = '-1'

db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
babel = Babel()

def configure_logging(app):
    """Configure logging for the application"""
    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Application startup")

def register_error_handlers(app):
    """Register Error Handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f"Page not found: {request.url}")
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Server Error: {error}")
        return render_template("errors/500.html"), 500

def configure_security(app):
    """Configure security headers and options"""
    @app.after_request
    def add_security_headers(response):
        """Add security headers to response"""
        if not app.debug:  # Only apply in production
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'

            # Only add HSTS in production
            if app.config.get('FORCE_HTTPS'):
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
                response.headers['Content-Security-Policy'] = "default-src 'self'"

        return response

    @app.before_request
    def force_https():
        """Force HTTPS in production"""
        if app.config.get('FORCE_HTTPS') and not app.debug:
            if not request.is_secure:
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)


def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__, instance_relative_config=True)
    # Disable SSL completely for development
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['REMEMBER_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = None

    # Force HTTP
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Load configurations
    from config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Add this to disable SSL redirect in development
    @app.before_request
    def force_https():
        if app.config.get('FORCE_HTTPS') and not app.debug:
            if not request.is_secure:
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)

    # Add this to override security headers for development
    @app.after_request
    def after_request(response):
        response.headers.pop('Server', None)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

        # Remove strict security headers in development
        if app.debug:
            response.headers.pop('Strict-Transport-Security', None)
            response.headers.pop('Content-Security-Policy', None)

        return response

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    babel.init_app(app)

    # Configure components
    configure_logging(app)
    configure_security(app)
    register_error_handlers(app)

    # Register routes and blueprints via `init_routes`
    init_routes(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    return app

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        from .models import User
        return User.query.get(int(user_id))
    except Exception as e:
        current_app.logger.error(f"Error loading user {user_id}: {str(e)}")
        return None
