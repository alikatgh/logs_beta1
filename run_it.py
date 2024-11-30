#!/usr/bin/env python3
import os
import sys
from app import create_app

# Add the project directory to the Python path
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)


# Unset problematic environment variables
os.environ.pop('WERKZEUG_SERVER_FD', None)
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

app = create_app('development')

if __name__ == '__main__':
    try:
        app.run(
            host='localhost',
            port=5000,
            debug=True,
            use_reloader=False
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
