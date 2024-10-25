from flask import Flask, _

app = Flask(__name__)


@app.route('/')
def index():
    return _("Hello, World!")
