"""Return management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, make_response
from flask_login import login_required
from app.extensions import db
from app.models import Return, ReturnItem, Supermarket, Subchain, Product
from app.forms import ReturnForm
import csv
from io import StringIO

return_bp = Blueprint('return', __name__, url_prefix='/return')


@return_bp.route('/')
@login_required
def index():
    """List all returns."""
    returns = Return.query.order_by(Return.return_date.desc()).all()
    return render_template('return/index.html', returns=returns)


@return_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new return."""
    form = ReturnForm()
    
    # Get all products
    products = Product.query.order_by('name').all()
    product_choices = [(p.id, f"{p.name} (${p.price})") for p in products]
    
    # Populate select fields with actual data
    form.supermarket_id.choices = [(0, 'Select Supermarket')] + [
        (s.id, s.name) for s in Supermarket.query.order_by('name').all()
    ]
    
    # If supermarket is selected, populate subchains
    if form.supermarket_id.data:
        subchains = Subchain.query.filter_by(supermarket_id=form.supermarket_id.data).all()
        form.subchain_id.choices = [(0, 'Select Subchain')] + [
            (s.id, s.name) for s in subchains
        ]
    
    # Populate product choices for each product form
    for product_form in form.products:
        product_form.product_id.choices = [(0, 'Select Product')] + product_choices
    
    if form.validate_on_submit():
        try:
            return_obj = Return(
                delivery_date=form.delivery_date.data,
                return_date=form.return_date.data,
                supermarket_id=form.supermarket_id.data,
                subchain_id=form.subchain_id.data if form.subchain_id.data and form.subchain_id.data != 0 else None
            )
            
            for product_form in form.products:
                if product_form.product_id.data and product_form.product_id.data != 0:
                    item = ReturnItem(
                        product_id=product_form.product_id.data,
                        quantity=product_form.quantity.data,
                        price=product_form.price.data
                    )
                    return_obj.items.append(item)
            
            if not return_obj.items:
                flash('Please add at least one product', 'error')
                return render_template('return/create.html', form=form)
            
            db.session.add(return_obj)
            db.session.commit()
            flash('Return created successfully', 'success')
            return redirect(url_for('return.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating return: {str(e)}', 'error')
    
    return render_template('return/create.html', form=form)


@return_bp.route('/<int:return_id>')
@login_required
def view(return_id):
    """View a specific return."""
    return_obj = Return.query.get_or_404(return_id)
    return render_template('return/view.html', return_obj=return_obj)


@return_bp.route('/download')
@login_required
def download():
    """Download returns as CSV."""
    # Get data
    returns = Return.query.order_by(Return.return_date.desc()).all()
    
    # Create CSV file
    si = StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(['Return Date', 'Delivery Date', 'Supermarket', 'Subchain', 'Products', 'Total Value (₮)'])
    
    # Write returns
    for return_obj in returns:
        products = ", ".join([
            f"{item.product.name} ({item.quantity} x ₮{item.price})"
            for item in return_obj.items
        ])
        
        writer.writerow([
            return_obj.return_date.strftime('%Y-%m-%d'),
            return_obj.delivery_date.strftime('%Y-%m-%d'),
            return_obj.supermarket.name,
            return_obj.subchain.name if return_obj.subchain else 'N/A',
            products,
            f"{return_obj.total_value:.2f}"
        ])
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=returns.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output
