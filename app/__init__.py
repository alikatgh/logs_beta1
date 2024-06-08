# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .database import db  # Correct import of the single db instance

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    # Initialize SQLAlchemy with the app
    db.init_app(app)
    # Initialize Flask-Migrate with the app and SQLAlchemy db
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
