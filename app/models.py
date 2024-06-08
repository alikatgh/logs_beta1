# app/models.py
from .database import db

class Supermarket(db.Model):
    __tablename__ = 'supermarket'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    deliveries = db.relationship('Delivery', back_populates='supermarket', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_items = db.relationship('DeliveryItem', back_populates='product', lazy=True)

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(db.Date, nullable=False)
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    supermarket = db.relationship('Supermarket', back_populates='deliveries')
    items = db.relationship('DeliveryItem', back_populates='delivery', cascade='all, delete-orphan')

class DeliveryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery = db.relationship('Delivery', back_populates='items')
    product = db.relationship('Product', back_populates='delivery_items')
