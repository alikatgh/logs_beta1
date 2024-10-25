from flask import render_template
from flask_login import login_required
from . import main  # Changed from 'app.routes import main'
from ..utils.decorators import log_action  # Changed from 'app.utils.decorators'


@main.route("/")
@login_required
@log_action("viewed_index")
def index():
    """Main index page"""
    return render_template("index.html")
