from flask import Blueprint, jsonify
from flask_login import login_required
from app.models import Delivery, Product, Supermarket

api = Blueprint("api", __name__)


@api.route("/products", methods=["GET"])
@login_required
def get_products():
    """Get all products"""
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])


@api.route("/supermarkets", methods=["GET"])
@login_required
def get_supermarkets():
    """Get all supermarkets"""
    supermarkets = Supermarket.query.all()
    return jsonify(
        [{"id": s.id, "name": s.name, "address": s.address} for s in supermarkets]
    )


@api.route("/deliveries", methods=["GET"])
@login_required
def get_deliveries():
    """Get all deliveries"""
    deliveries = Delivery.query.all()
    return jsonify([delivery.to_dict() for delivery in deliveries])
