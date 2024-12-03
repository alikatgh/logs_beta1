from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager
from datetime import datetime
from decimal import Decimal


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Supermarket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Relationships with cascade delete
    subchains = db.relationship('Subchain', backref='supermarket', lazy=True,
                               cascade='all, delete-orphan')
    deliveries = db.relationship('Delivery', backref='supermarket', lazy=True,
                                cascade='all, delete-orphan')
    returns = db.relationship('Return', backref='supermarket', lazy=True,
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Supermarket {self.name}>'


class Subchain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    
    # Relationships
    deliveries = db.relationship('Delivery', backref='subchain', lazy=True)
    returns = db.relationship('Return', backref='subchain', lazy=True)

    def __repr__(self):
        return f'<Subchain {self.name}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    weight = db.Column(db.Numeric(10, 3), nullable=False)  # Weight in kg
    
    # Relationships with cascade delete
    delivery_items = db.relationship(
        'DeliveryItem',
        backref='product',
        lazy=True,
        cascade='all, delete-orphan'
    )
    return_items = db.relationship(
        'ReturnItem',
        backref='product',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Product {self.name}>'


class Delivery(db.Model):
    __tablename__ = 'delivery'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    subchain_id = db.Column(db.Integer, db.ForeignKey('subchain.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship(
        'DeliveryItem',
        backref='delivery',
        lazy=True,
        cascade='all, delete-orphan'
    )

    @property
    def total_value(self):
        return sum(item.total_price for item in self.items)

    def __repr__(self):
        return f'<Delivery {self.id} to {self.supermarket.name if self.supermarket else "Unknown"}>'


class DeliveryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def total_price(self):
        return Decimal(str(self.price)) * self.quantity

    def __repr__(self):
        return f'<DeliveryItem {self.product.name} x{self.quantity}>'


class Return(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarket.id'), nullable=False)
    subchain_id = db.Column(db.Integer, db.ForeignKey('subchain.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship(
        'ReturnItem',
        backref='return_obj',
        lazy=True,
        cascade='all, delete-orphan'
    )

    @property
    def total_value(self):
        return sum(item.total_price for item in self.items)

    def __repr__(self):
        return f'<Return {self.id} from {self.supermarket.name if self.supermarket else "Unknown"}>'


class ReturnItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('return.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def total_price(self):
        return Decimal(str(self.price)) * self.quantity

    def __repr__(self):
        return f'<ReturnItem {self.product.name} x{self.quantity}>'
