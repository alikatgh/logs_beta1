from waitress import serve
from app import create_app

app = create_app('development')

if __name__ == '__main__':
    print("Starting server on http://localhost:5000")
    serve(app, host='localhost', port=5000)
