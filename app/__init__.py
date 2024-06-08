# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .database import db  # Correct import of the single db instance
from .models import User  # Import the User model here

from flask_wtf import CSRFProtect

csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    # Initialize SQLAlchemy with the app
    db.init_app(app)
    # Initialize Flask-Migrate with the app and SQLAlchemy db
    migrate.init_app(app, db)
    # Initialize LoginManager with the app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Set the default login view for @login_required

    with app.app_context():
        db.create_all()

    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .auth_routes import auth as auth_blueprint  # import your auth blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')  # register the auth blueprint

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
