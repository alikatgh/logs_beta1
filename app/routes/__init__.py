from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import CSRFError

# Define __all__ for explicit exports
__all__ = ["init_app", "main", "auth", "product", "supermarket", "delivery", "report"]

# Create blueprints
main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)
product = Blueprint("product", __name__)
supermarket = Blueprint("supermarket", __name__)
delivery = Blueprint("delivery", __name__)
report = Blueprint("report", __name__)


def register_csrf_handler(flask_app):
    """Register CSRF error handler"""
    @flask_app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """Handle CSRF token errors"""
        flask_app.logger.warning(f"CSRF error: {e}")
        if request.is_json:
            return jsonify(error="CSRF token missing or invalid"), 400
        return render_template("errors/csrf_error.html"), 400


def init_app(flask_app):
    """
    Initialize routes with the app

    Args:
        flask_app: Flask application instance
    """
    # Import views here to avoid circular imports
    # These imports are used for their side effects (registering routes)
    from . import main_routes  # noqa
    from . import auth_routes  # noqa

    # Import error handlers
    from .error_handlers import register_error_handlers

    # Register blueprints
    blueprints = [
        (main, ''),
        (auth, '/auth'),
        (product, '/products'),
        (supermarket, '/supermarkets'),
        (delivery, '/deliveries'),
        (report, '/reports')
    ]

    for blueprint, url_prefix in blueprints:
        flask_app.register_blueprint(blueprint, url_prefix=url_prefix)

    flask_app.logger.info("Registered blueprints")

    # Register error handlers (only once)
    register_error_handlers(flask_app)
    register_csrf_handler(flask_app)

    return flask_app
