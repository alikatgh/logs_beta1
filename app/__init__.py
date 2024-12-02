"""Flask application initialization."""
from flask import Flask
from config import Config
from app.extensions import db, login_manager, mail


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints here
    from app.auth_routes import auth_bp
    from app.main_routes import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app


# Create the app instance with default configuration
app = create_app()
