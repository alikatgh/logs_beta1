"""Delivery management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, make_response, request
from flask_login import login_required
from app.extensions import db
from app.models import Delivery, DeliveryItem, Product, Supermarket, Subchain
from app.forms import DeliveryForm
import csv
from io import StringIO
from flask_wtf import FlaskForm

# Create the blueprint
delivery_bp = Blueprint('delivery', __name__, url_prefix='/delivery')


@delivery_bp.route('/')
@login_required
def index():
    """List all deliveries."""
    deliveries = Delivery.query.order_by(Delivery.delivery_date.desc()).all()
    form = FlaskForm()
    return render_template('delivery/index.html', deliveries=deliveries, form=form)


@delivery_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new delivery."""
    form = DeliveryForm()
    
    # Populate select fields with actual data
    form.supermarket_id.choices = [
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
        product_form.product_id.choices = [
            (p.id, f"{p.name} (${p.price})") 
            for p in Product.query.order_by('name').all()
        ]
    
    if form.validate_on_submit():
        try:
            delivery = Delivery(
                delivery_date=form.delivery_date.data,
                supermarket_id=form.supermarket_id.data,
                subchain_id=form.subchain_id.data if form.subchain_id.data and form.subchain_id.data != 0 else None
            )
            
            for product_form in form.products:
                if product_form.product_id.data:
                    item = DeliveryItem(
                        product_id=product_form.product_id.data,
                        quantity=product_form.quantity.data,
                        price=product_form.price.data
                    )
                    delivery.items.append(item)
            
            if not delivery.items:
                flash('Please add at least one product', 'error')
                return render_template('delivery/create.html', form=form)
            
            db.session.add(delivery)
            db.session.commit()
            flash('Delivery created successfully', 'success')
            return redirect(url_for('delivery.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating delivery: {str(e)}', 'error')
    
    return render_template('delivery/create.html', form=form)


@delivery_bp.route('/<int:delivery_id>')
@login_required
def view(delivery_id):
    """View a specific delivery."""
    delivery = Delivery.query.get_or_404(delivery_id)
    return render_template('delivery/view.html', delivery=delivery)


@delivery_bp.route('/get_subchains/<int:supermarket_id>')
@login_required
def get_subchains(supermarket_id):
    """Get subchains for a supermarket (AJAX endpoint)."""
    subchains = Subchain.query.filter_by(supermarket_id=supermarket_id).all()
    return jsonify([
        {'id': s.id, 'name': s.name} for s in subchains
    ])


@delivery_bp.route('/get_products')
@login_required
def get_products():
    """Get all products (AJAX endpoint)."""
    products = Product.query.order_by('name').all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': float(p.price) if p.price else 0
    } for p in products])


@delivery_bp.route('/download')
@login_required
def download():
    """Download deliveries as CSV."""
    # Get data
    deliveries = Delivery.query.order_by(Delivery.delivery_date.desc()).all()
    
    # Create CSV file
    si = StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(['Date', 'Supermarket', 'Subchain', 'Products', 'Total Value (₮)'])
    
    # Write deliveries
    for delivery in deliveries:
        products = ", ".join([
            f"{item.product.name} ({item.quantity} x ₮{item.price})"
            for item in delivery.items
        ])
        
        writer.writerow([
            delivery.delivery_date.strftime('%Y-%m-%d'),
            delivery.supermarket.name,
            delivery.subchain.name if delivery.subchain else 'N/A',
            products,
            f"{delivery.total_value:.2f}"
        ])
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=deliveries.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output 


@delivery_bp.route('/<int:delivery_id>/delete', methods=['POST'])
@login_required
def delete_delivery(delivery_id):
    """Delete a delivery."""
    delivery = Delivery.query.get_or_404(delivery_id)
    try:
        db.session.delete(delivery)
        db.session.commit()
        flash('Delivery deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting delivery: {str(e)}', 'error')
    return redirect(url_for('delivery.index'))


@delivery_bp.route('/bulk_delete', methods=['POST'])
@login_required
def bulk_delete_deliveries():
    """Delete multiple deliveries."""
    delivery_ids = request.form.getlist('selected_deliveries[]')
    if not delivery_ids:
        flash('No deliveries selected', 'error')
        return redirect(url_for('delivery.index'))
    
    try:
        deliveries = Delivery.query.filter(Delivery.id.in_(delivery_ids)).all()
        for delivery in deliveries:
            db.session.delete(delivery)
        db.session.commit()
        flash(f'{len(deliveries)} deliveries deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting deliveries: {str(e)}', 'error')
    return redirect(url_for('delivery.index')) 