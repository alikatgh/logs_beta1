"""Product management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Product
from app.forms import ProductForm
from flask_wtf import FlaskForm

product_bp = Blueprint('product', __name__, url_prefix='/product')


@product_bp.route('/')
@login_required
def manage_products():
    """List and manage products."""
    products = Product.query.order_by(Product.name).all()
    form = FlaskForm()
    return render_template('products/manage_products.html', products=products, form=form)


@product_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new product."""
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            weight=form.weight.data
        )
        try:
            db.session.add(product)
            db.session.commit()
            flash('Product created successfully', 'success')
            return redirect(url_for('product.manage_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating product: {str(e)}', 'error')
    return render_template('products/create.html', form=form)


@product_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """Edit a product."""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        try:
            product.name = form.name.data
            product.price = form.price.data
            product.weight = form.weight.data
            db.session.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('product.manage_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')
    
    return render_template('products/edit.html', form=form, product=product)


@product_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    """Delete a product."""
    product = Product.query.get_or_404(id)
    try:
        # Get related deliveries and returns
        delivery_count = sum(len(item.delivery.items) for item in product.delivery_items)
        return_count = sum(len(item.return_obj.items) for item in product.return_items)
        
        if delivery_count > 0 or return_count > 0:
            flash(
                f'Cannot delete product "{product.name}" because it is used in '
                f'{delivery_count} deliveries and {return_count} returns. '
                'Please remove it from all deliveries and returns first.',
                'error'
            )
        else:
            db.session.delete(product)
            db.session.commit()
            flash('Product deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
    return redirect(url_for('product.manage_products'))
