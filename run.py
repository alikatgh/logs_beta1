from app import app

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except RuntimeError:  # Specifically catch Werkzeug runtime errors
        import os
        # Force cleanup of any existing server
        if 'WERKZEUG_SERVER_FD' in os.environ:
            del os.environ['WERKZEUG_SERVER_FD']
        # Try running again
        app.run(debug=True)