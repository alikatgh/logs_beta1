# app/models.py
from .database import db

class Supermarket(db.Model):
    __tablename__ = 'supermarket'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    deliveries = db.relationship('Delivery', backref='supermarket', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_items = db.relationship('DeliveryItem', backref='product', lazy=True)

class Delivery(db.Model):
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(db.Date, nullable=False)
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    items = db.relationship('DeliveryItem', backref='delivery', lazy=True)

class DeliveryItem(db.Model):
    __tablename__ = 'delivery_item'
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
