"""Product management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Product
from app.forms import ProductForm

product_bp = Blueprint('product', __name__, url_prefix='/product')


@product_bp.route('/')
@login_required
def manage_products():
    """List and manage products."""
    products = Product.query.order_by(Product.name).all()
    return render_template('products/manage_products.html', products=products)


@product_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new product."""
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            sku=form.sku.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product created successfully', 'success')
        return redirect(url_for('product.manage_products'))
    return render_template('products/create.html', form=form)


@product_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a product."""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.sku = form.sku.data
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('product.manage_products'))
    
    return render_template('products/edit.html', form=form, product=product)
