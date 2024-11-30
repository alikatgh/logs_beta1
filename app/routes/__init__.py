from flask import Blueprint, render_template
from flask_wtf.csrf import CSRFError

__all__ = ["init_app", "main", "auth", "product", "supermarket", "delivery", "report", "return_"]

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)
product = Blueprint("product", __name__)
supermarket = Blueprint("supermarket", __name__)
delivery = Blueprint("delivery", __name__)
report = Blueprint("report", __name__)
return_ = Blueprint("return", __name__)


def register_csrf_handler(flask_app):
    @flask_app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template("errors/csrf_error.html"), 400


def init_app(flask_app):
    # from . import main_routes, auth_routes, delivery_routes, return_routes, product_routes, supermarket_routes, report_routes
    from .error_handlers import register_error_handlers

    blueprints = [
        (main, ''),
        (auth, '/auth'),
        (product, '/products'),
        (supermarket, '/supermarkets'),
        (delivery, '/deliveries'),
        (report, '/reports'),
        (return_, '/returns')
    ]

    for blueprint, url_prefix in blueprints:
        flask_app.register_blueprint(blueprint, url_prefix=url_prefix)

    register_error_handlers(flask_app)
    register_csrf_handler(flask_app)
    return flask_app
