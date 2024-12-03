"""Flask application initialization."""
from flask import Flask
from flask_migrate import Migrate
from config import Config
from app.extensions import db, login_manager, mail
from app.routes import (
    auth_bp,
    main_bp,
    delivery_bp,
    return_bp,
    product_bp,
    supermarket_bp,
    report_bp
)
from flask_wtf.csrf import CSRFProtect


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    Migrate(app, db)
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(return_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(supermarket_bp)
    app.register_blueprint(report_bp)

    return app


# Create the app instance with default configuration
app = create_app()
