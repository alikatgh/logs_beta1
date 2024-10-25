from app import create_app, db
from app.models import User, Supermarket, Subchain, Product, Delivery, DeliveryItem

app = create_app()


def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database has been reset.")


def create_tables():
    with app.app_context():
        db.create_all()
        print("Tables have been created.")


def list_tables():
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print("Tables in the database:")
        for table in tables:
            print(f"- {table}")
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"  - {column['name']}: {column['type']}")


def print_model_info():
    with app.app_context():
        print("Model information:")
        for model in [User, Supermarket, Subchain, Product, Delivery, DeliveryItem]:
            print(f"{model.__name__}: {model.__table__.name}")
            for column in model.__table__.columns:
                print(f"  - {column.name}: {column.type}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "reset":
            reset_db()
        elif sys.argv[1] == "create":
            create_tables()
        elif sys.argv[1] == "list":
            list_tables()
        elif sys.argv[1] == "info":
            print_model_info()
    else:
        print("Usage: python manage_db.py [reset|create|list|info]")
