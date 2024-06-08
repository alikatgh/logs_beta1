import os
from datetime import timedelta

SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///deliveries.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Login configuration
LOGIN_VIEW = 'auth.login'
REMEMBER_COOKIE_DURATION = timedelta(days=7)
