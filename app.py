from flask import Flask
from flask_cors import CORS
from models import db
import os

app = Flask(__name__)

# -----------------------------
# 🔗 Supabase PostgreSQL Connection
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Njugunaa1!1@db.qkwkheukgubkqqccyzpu.supabase.co:5432/postgres?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

# Allow CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize DB
db.init_app(app)

# Blueprints
from routes import events, sermons
app.register_blueprint(events.bp)
app.register_blueprint(sermons.bp)

# Health Check
@app.route('/health')
def health():
    return 'OK', 200

# Create tables + uploads folder
with app.app_context():
    db.create_all()
    uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
