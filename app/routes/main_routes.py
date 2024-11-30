from flask import render_template
from flask_login import login_required
from . import main  # Import the blueprint from __init__.py instead of creating new one
from ..utils.decorators import log_action


@main.route("/")
@login_required
@log_action("viewed_index")
def index():
    """Main index page"""
    return render_template("index.html")
