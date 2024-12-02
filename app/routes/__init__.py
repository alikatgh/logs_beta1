"""Routes package initialization."""
from app.routes.auth_routes import auth_bp
from app.routes.main_routes import main_bp
from app.routes.delivery_routes import delivery_bp
from app.routes.return_routes import return_bp
from app.routes.product_routes import product_bp
from app.routes.supermarket_routes import supermarket_bp
from app.routes.report_routes import report_bp

__all__ = [
    'auth_bp',
    'main_bp',
    'delivery_bp',
    'return_bp',
    'product_bp',
    'supermarket_bp',
    'report_bp'
]
