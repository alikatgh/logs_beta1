from flask import render_template
from flask_login import login_required

from app.routes import return_  # Import blueprint from routes/__init__.py


@return_.route("/")
@login_required
def index():
    """Display list of returns"""
    return render_template("returns/index.html")


@return_.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new return"""
    return render_template("returns/create.html")
