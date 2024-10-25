import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, jsonify, current_app, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException
from flask_mail import Mail

# Import models after db is defined to avoid circular imports
from .models import User

db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()  # Add this line


def configure_logging(app):
    """Configure logging for the application"""
    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=10240000, backupCount=10
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Application startup")


def register_error_handlers(app):
    """Register Error Handlers"""

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        app.logger.error(f"CSRF error: {e}")
        return render_template("errors/csrf_error.html"), 400

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f"Page not found: {request.url}")
        if request.is_json:
            return jsonify(error="Resource not found"), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Server Error: {error}")
        if request.is_json:
            return jsonify(error="Internal server error"), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return e

        # Log the error
        app.logger.error(f"Unhandled exception: {str(e)}")

        # Return JSON for API requests
        if request.is_json:
            return jsonify(error="Internal server error"), 500

        # Return HTML for browser requests
        return render_template("errors/500.html"), 500


def register_blueprints(app):
    """Register Flask blueprints"""
    from .routes import main, auth

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(auth, url_prefix="/auth")

    app.logger.info("Registered blueprints")


def configure_security(app):
    """Configure security headers and options"""
    @app.after_request
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Only add HSTS in production
        if not app.debug and not app.testing:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response

    @app.before_request
    def force_https():
        """Force HTTPS in production"""
        if (not app.debug and not app.testing and not request.is_secure and app.config.get('ENV') == 'production'):

            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)


def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__, instance_relative_config=True)

    # Import config at runtime to avoid circular imports
    from config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)  # Call the init_app method of the config class

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
        app.logger.info(f"Created instance folder: {app.instance_path}")
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)  # Add this line

    if app.debug:
        DebugToolbarExtension(app)

    # Configure components
    configure_logging(app)
    configure_security(app)
    register_error_handlers(app)
    # register_blueprints(app)

    # Register routes and blueprints (only once)
    from app.routes import init_app as init_routes
    init_routes(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Database initialization
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise

        # Log database schema
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        app.logger.info("Current database schema:")
        for table in tables:
            columns = inspector.get_columns(table)
            app.logger.info(f"Table: {table}")
            for column in columns:
                app.logger.info(f"  - {column['name']}: {column['type']}")

    return app


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        current_app.logger.error(f"Error loading user {user_id}: {str(e)}")
        return None
