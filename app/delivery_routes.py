"""Delivery management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import Delivery, DeliveryItem, Product, Supermarket, Subchain
from app.forms import DeliveryForm

# Create the blueprint
delivery_bp = Blueprint('delivery', __name__, url_prefix='/delivery')


@delivery_bp.route('/')
@login_required
def index():
    """List all deliveries."""
    deliveries = Delivery.query.order_by(Delivery.delivery_date.desc()).all()
    return render_template('delivery/index.html', deliveries=deliveries)


@delivery_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new delivery."""
    form = DeliveryForm()
    
    # Populate select fields
    form.supermarket_id.choices = [
        (s.id, s.name) for s in Supermarket.query.order_by('name')
    ]
    
    if form.validate_on_submit():
        delivery = Delivery(
            delivery_date=form.delivery_date.data,
            supermarket_id=form.supermarket_id.data,
            subchain_id=form.subchain.data if form.subchain.data else None
        )
        
        for product_form in form.products:
            item = DeliveryItem(
                product_id=product_form.product_id.data,
                quantity=product_form.quantity.data,
                price=product_form.price.data
            )
            delivery.items.append(item)
        
        db.session.add(delivery)
        db.session.commit()
        flash('Delivery created successfully', 'success')
        return redirect(url_for('delivery.index'))
    
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
    return jsonify([{'id': s.id, 'name': s.name} for s in subchains])


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