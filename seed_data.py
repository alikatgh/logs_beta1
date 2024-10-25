from app import db, create_app  # Import your app creation function and db
from app.models import Supermarket, Product


def seed_data():
    supermarket1 = Supermarket(name='Supermarket 1', address='Address 1')
    supermarket2 = Supermarket(name='Supermarket 2', address='Address 2')
    db.session.add(supermarket1)
    db.session.add(supermarket2)

    product1 = Product(name='Product 1', price=10.0)
    product2 = Product(name='Product 2', price=15.0)
    db.session.add(product1)
    db.session.add(product2)

    db.session.commit()
    print("Data seeded successfully.")


if __name__ == '__main__':
    app = create_app()  # Create an instance of your Flask app
    with app.app_context():  # Push the app context
        seed_data()
