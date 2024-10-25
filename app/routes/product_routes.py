from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.routes import product
from app.models import Product
from app.database import db


@product.route("/", methods=["GET", "POST"])
@login_required
def manage_products():
    """Handle product management"""
    if request.method == "POST":
        try:
            names = request.form.getlist("name[]")
            prices = request.form.getlist("price[]")

            for name, price in zip(names, prices):
                new_product = Product(name=name, price=price)
                db.session.add(new_product)
            db.session.commit()
            flash("Products added successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding products: {str(e)}", "danger")

    products = Product.query.all()
    return render_template("manage_products.html", products=products)


@product.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product(id):
    """Handle product editing"""
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        try:
            product.name = request.form["name"]
            product.price = request.form["price"]
            db.session.commit()
            flash("Product updated successfully", "success")
            return redirect(url_for("product.manage_products"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating product: {str(e)}", "danger")

    return render_template("edit_products.html", product=product)


@product.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_product(id):
    """Handle product deletion"""
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting product: {str(e)}", "danger")

    return redirect(url_for("product.manage_products"))
