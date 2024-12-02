from app import app, db
from app.models import User, Supermarket, Subchain, Product

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin')  # Change this password in production!
            db.session.add(admin)
            
            # Create sample supermarket
            supermarket = Supermarket(
                name='Sample Supermarket',
                address='123 Main St',
                contact_person='John Doe',
                phone='555-0123',
                email='contact@sample.com'
            )
            db.session.add(supermarket)
            
            # Create sample subchain
            subchain = Subchain(
                name='Downtown Branch',
                supermarket=supermarket
            )
            db.session.add(subchain)
            
            # Create sample product
            product = Product(
                name='Sample Product',
                description='A sample product description',
                price=9.99,
                sku='SAMPLE001'
            )
            db.session.add(product)
            
            db.session.commit()
            print("Database initialized with sample data")
        else:
            print("Database already contains data")

if __name__ == '__main__':
    init_db()
