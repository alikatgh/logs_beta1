from flask import Blueprint, render_template, make_response
from flask_login import login_required
from app.models import Delivery, Return
import csv
from io import StringIO


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


@report_bp.route('/download')
@login_required
def download():
    """Download report as CSV."""
    # Get data
    deliveries = Delivery.query.order_by(Delivery.delivery_date.desc()).all()
    returns = Return.query.order_by(Return.return_date.desc()).all()
    
    # Create CSV file
    si = StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(['Report Type', 'Date', 'Supermarket', 'Subchain', 'Total Value (₮)'])
    
    # Write deliveries
    for delivery in deliveries:
        writer.writerow([
            'Delivery',
            delivery.delivery_date.strftime('%Y-%m-%d'),
            delivery.supermarket.name,
            delivery.subchain.name if delivery.subchain else 'N/A',
            f"{delivery.total_value:.2f}"
        ])
    
    # Write returns
    for return_obj in returns:
        writer.writerow([
            'Return',
            return_obj.return_date.strftime('%Y-%m-%d'),
            return_obj.supermarket.name,
            return_obj.subchain.name if return_obj.subchain else 'N/A',
            f"{return_obj.total_value:.2f}"
        ])
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output
