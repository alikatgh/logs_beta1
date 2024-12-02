from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Delivery, Return


report_bp = Blueprint('report', __name__, url_prefix='/report')


@report_bp.route('/generate')
@login_required
def generate_report():
    """Generate delivery and return reports."""
    deliveries = Delivery.query.order_by(Delivery.delivery_date.desc()).all()
    returns = Return.query.order_by(Return.return_date.desc()).all()
    return render_template(
        'report/generate.html',
        deliveries=deliveries,
        returns=returns
    )
