from app import create_app, db
from app.models import User, Supermarket, Subchain, Product, Delivery, DeliveryItem

app = create_app()

with app.app_context():
    print("Metadata tables:")
    for table in db.metadata.tables:
        print(f"- {table}")

    print("\nAttempting to create tables...")
    db.create_all()
    print("Tables created.")

    print("\nChecking created tables:")
    inspector = db.inspect(db.engine)
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
        for column in inspector.get_columns(table_name):
            print(f"  - {column['name']}: {column['type']}")

    print("\nAttempting to create a test user...")
    try:
        new_user = User(username="test_user", email="test@example.com")
        new_user.set_password("password123")
        db.session.add(new_user)
        db.session.commit()
        print("Test user created successfully")
    except Exception as e:
        print(f"Error creating test user: {str(e)}")

print("\nDatabase URI:", app.config['SQLALCHEMY_DATABASE_URI'])
