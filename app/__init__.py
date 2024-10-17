from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from .database import db
from .models import User
import os
from datetime import timedelta

csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///deliveries.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGIN_VIEW = 'auth.login'
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    WTF_CSRF_ENABLED = True
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .auth_routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
