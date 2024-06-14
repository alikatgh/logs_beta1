from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .database import db

class Supermarket(db.Model):
    __tablename__ = 'supermarket'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    deliveries = db.relationship('Delivery', back_populates='supermarket', lazy=True)
    subchains = db.relationship('Subchain', back_populates='supermarket', lazy=True)

class Subchain(db.Model):
    __tablename__ = 'subchain'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    supermarket = db.relationship('Supermarket', back_populates='subchains')

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_items = db.relationship('DeliveryItem', back_populates='product', lazy=True)

class Delivery(db.Model):
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(db.Date, nullable=False)
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    subchain_id = db.Column(db.Integer, db.ForeignKey('subchain.id'), nullable=True)
    is_return = db.Column(db.Boolean, default=False)
    supermarket = db.relationship('Supermarket', back_populates='deliveries')
    subchain = db.relationship('Subchain', backref='deliveries')
    items = db.relationship('DeliveryItem', back_populates='delivery', cascade='all, delete-orphan')

class DeliveryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery = db.relationship('Delivery', back_populates='items')
    product = db.relationship('Product', back_populates='delivery_items')

# login and register implementation

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
