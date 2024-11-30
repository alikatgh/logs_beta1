# from flask_sqlalchemy import SQLAlchemy
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import validates
from sqlalchemy import event
import re

# db = SQLAlchemy()


class TimestampMixin:
    """Mixin for adding timestamp fields to models"""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)

    # Add relationship to track user actions
    deliveries_created = db.relationship('Delivery', backref='created_by', lazy='dynamic')

    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email address")
        return email.lower()

    @validates('username')
    def validate_username(self, key, username):
        if not re.match(r"^[a-zA-Z0-9_]{3,80}$", username):
            raise ValueError("Username must be alphanumeric and between 3-80 characters")
        return username

    def set_password(self, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Supermarket(TimestampMixin, db.Model):
    __tablename__ = 'supermarket'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    deliveries = db.relationship(
        'Delivery',
        back_populates='supermarket',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    subchains = db.relationship(
        'Subchain',
        back_populates='supermarket',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @validates('name')
    def validate_name(self, key, name):
        if not name.strip():
            raise ValueError("Supermarket name cannot be empty")
        return name.strip()

    def __repr__(self):
        return f"<Supermarket {self.name}>"


class Subchain(TimestampMixin, db.Model):
    __tablename__ = 'subchain'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('name', 'supermarket_id', name='uix_name_supermarket'),
    )

    supermarket = db.relationship('Supermarket', back_populates='subchains')
    deliveries = db.relationship(
        'Delivery',
        back_populates='subchain',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @validates('name')
    def validate_name(self, key, name):
        if not name.strip():
            raise ValueError("Subchain name cannot be empty")
        return name.strip()

    def __repr__(self):
        return f"<Subchain {self.name} of Supermarket ID: {self.supermarket_id}>"


class Product(TimestampMixin, db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    delivery_items = db.relationship(
        'DeliveryItem',
        back_populates='product',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @validates('price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Product {self.name}>"


class Delivery(TimestampMixin, db.Model):
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True)
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    subchain_id = db.Column(db.Integer, db.ForeignKey('subchain.id'), nullable=True)
    delivery_date = db.Column(db.Date, nullable=False, index=True)
    return_date = db.Column(db.Date, nullable=True)
    is_return = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, delivered, returned, cancelled
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    supermarket = db.relationship('Supermarket', back_populates='deliveries')
    subchain = db.relationship('Subchain', back_populates='deliveries')
    items = db.relationship(
        'DeliveryItem',
        back_populates='delivery',
        # lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = {'pending', 'delivered', 'returned', 'cancelled'}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return status

    @property
    def total_amount(self):
        return sum(item.quantity * item.price for item in self.items)

    def to_dict(self):
        return {
            'id': self.id,
            'supermarket_id': self.supermarket_id,
            'subchain_id': self.subchain_id,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'is_return': self.is_return,
            'status': self.status,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Delivery ID: {self.id}, Status: {self.status}>"


class DeliveryItem(TimestampMixin, db.Model):
    __tablename__ = 'delivery_item'
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of delivery

    __table_args__ = (
        db.Index('idx_delivery_product', 'delivery_id', 'product_id'),
    )

    product = db.relationship('Product', back_populates='delivery_items')
    delivery = db.relationship('Delivery', back_populates='items')

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return quantity

    @validates('price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price

    def to_dict(self):
        return {
            'id': self.id,
            'delivery_id': self.delivery_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'total': self.quantity * self.price
        }

    def __repr__(self):
        return f"<DeliveryItem Product ID: {self.product_id}, Quantity: {self.quantity}>"


# Event listeners for automatic timestamp updates
@event.listens_for(db.Session, 'before_flush')
def update_timestamps(session, context, instances):
    for instance in session.dirty:
        if isinstance(instance, TimestampMixin):
            instance.updated_at = datetime.utcnow()
