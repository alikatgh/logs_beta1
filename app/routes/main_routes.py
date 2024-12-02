"""Main routes for the application."""
from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """Render the home page."""
    return render_template('index.html')
