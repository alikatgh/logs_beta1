import os
from app import create_app, db
from flask_migrate import Migrate

# Get environment or default to development
config_name = os.environ.get('FLASK_CONFIG', 'default')
app = create_app(config_name)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)