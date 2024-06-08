# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from .database import db
from .models import Delivery, DeliveryItem, Supermarket, Product

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/deliveries/create', methods=['GET', 'POST'])
def create_delivery():
    products = Product.query.all()
    supermarkets = Supermarket.query.all()

    if request.method == 'POST':
        try:
            delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d')
            supermarket_id = request.form['supermarket_id']

            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('quantity[]')
            prices = request.form.getlist('price[]')

            new_delivery = Delivery(
                supermarket_id=supermarket_id,
                delivery_date=delivery_date
            )
            db.session.add(new_delivery)
            db.session.flush()

            for product_id, quantity, price in zip(product_ids, quantities, prices):
                new_item = DeliveryItem(
                    delivery_id=new_delivery.id,
                    product_id=product_id,
                    quantity=quantity,
                    price=price
                )
                db.session.add(new_item)

            db.session.commit()
            flash('Delivery created successfully', 'success')
            return redirect(url_for('main.deliveries'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating delivery: {str(e)}', 'danger')

    return render_template('create_delivery.html', products=products, supermarkets=supermarkets)

@main.route('/deliveries', methods=['GET', 'POST'])
def deliveries():
    if request.method == 'POST':
        delivery_id = request.form.get('delivery_id')
        if delivery_id:
            return redirect(url_for('main.delete_delivery', delivery_id=delivery_id))
    deliveries = Delivery.query.all()
    return render_template('deliveries.html', deliveries=deliveries)

@main.route('/deliveries/<int:delivery_id>', methods=['GET'])
def delivery_details(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    return render_template('delivery_details.html', delivery=delivery)

@main.route('/report', methods=['GET'])
def report():
    return render_template('report.html')

@main.route('/supermarkets', methods=['GET', 'POST'])
def manage_supermarkets():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        new_supermarket = Supermarket(name=name, address=address)
        db.session.add(new_supermarket)
        db.session.commit()
        flash('Supermarket added successfully', 'success')
        return redirect(url_for('main.manage_supermarkets'))
    
    supermarkets = Supermarket.query.all()
    return render_template('manage_supermarkets.html', supermarkets=supermarkets)

@main.route('/supermarkets/edit/<int:id>', methods=['GET', 'POST'])
def edit_supermarket(id):
    supermarket = Supermarket.query.get_or_404(id)
    if request.method == 'POST':
        supermarket.name = request.form['name']
        supermarket.address = request.form['address']
        db.session.commit()
        flash('Supermarket updated successfully', 'success')
        return redirect(url_for('main.manage_supermarkets'))
    return render_template('edit_supermarket.html', supermarket=supermarket)

@main.route('/supermarkets/delete/<int:id>', methods=['POST'])
def delete_supermarket(id):
    supermarket = Supermarket.query.get_or_404(id)
    db.session.delete(supermarket)
    db.session.commit()
    flash('Supermarket deleted successfully', 'success')
    return redirect(url_for('main.manage_supermarkets'))

@main.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        new_product = Product(name=name, price=price)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('main.manage_products'))
    
    products = Product.query.all()
    return render_template('manage_products.html', products=products)

@main.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('main.manage_products'))
    return render_template('edit_product.html', product=product)

@main.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully', 'success')
    return redirect(url_for('main.manage_products'))

@main.route('/deliveries/delete/<int:delivery_id>', methods=['POST'])
def delete_delivery(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    db.session.delete(delivery)
    db.session.commit()
    flash('Delivery deleted successfully', 'success')
    return redirect(url_for('main.deliveries'))
