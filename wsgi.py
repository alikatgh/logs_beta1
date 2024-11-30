from app import create_app
from werkzeug.serving import run_simple

application = create_app('development')

if __name__ == "__main__":
    import os
    import sys

    # Add the current directory to Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # Run the application
    try:
        run_simple(
            'localhost',
            5000,
            application,
            use_reloader=True,
            use_debugger=True,
            threaded=True
        )
    except KeyError as e:
        # If WERKZEUG_SERVER_FD error occurs, try alternative method
        application.run(
            host='localhost',
            port=5000,
            debug=True,
            use_reloader=False
        )
