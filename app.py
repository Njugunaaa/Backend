from flask import Flask
from flask_cors import CORS
from models import db
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

CORS(app, resources={r"/api/*": {"origins": "*"}})

db.init_app(app)

from routes import events, sermons

app.register_blueprint(events.bp)
app.register_blueprint(sermons.bp)

with app.app_context():
    db.create_all()
    uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
