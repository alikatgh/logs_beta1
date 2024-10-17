import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///deliveries.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Login configuration
    LOGIN_VIEW = 'auth.login'
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # WTForms configuration
    WTF_CSRF_ENABLED = True

    # Flask-Session configuration (if you're using it)
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
