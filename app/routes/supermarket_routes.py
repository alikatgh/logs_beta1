from flask import render_template
from flask_login import login_required

from app.routes import supermarket


@supermarket.route("/")
@login_required
def index():
    """Display list of supermarkets"""
    return render_template("supermarkets/index.html")


@supermarket.route("/manage")
@login_required
def manage():
    """Manage supermarkets"""
    return render_template("supermarkets/manage.html")
