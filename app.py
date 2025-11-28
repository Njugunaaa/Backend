# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Event, Sermon
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# -----------------------------
# 🔗 Supabase REST Config
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")  # e.g. https://yourproject.supabase.co/rest/v1
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Service Role Key
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# -----------------------------
# Uploads folder (for events images)
# -----------------------------
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# Routes: Events
# -----------------------------
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        r = requests.get(f"{SUPABASE_URL}/events", headers=HEADERS)
        r.raise_for_status()
        events = [Event(d).to_dict() for d in r.json()]
        return jsonify(events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events", methods=["POST"])
def create_event():
    file = request.files.get("image")
    image_url = None

    if file:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        image_url = f"/static/uploads/{filename}"  # returned to frontend

    payload = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "image_path": image_url,
        "date": request.form.get("date"),
        "time": request.form.get("time"),
        "location": request.form.get("location"),
        "category": request.form.get("category")
    }

    try:
        r = requests.post(f"{SUPABASE_URL}/events", headers=HEADERS, json=payload)
        r.raise_for_status()
        return jsonify(Event(r.json()).to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Routes: Sermons
# -----------------------------
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    try:
        r = requests.get(f"{SUPABASE_URL}/sermons", headers=HEADERS)
        r.raise_for_status()
        sermons = [Sermon(d).to_dict() for d in r.json()]
        return jsonify(sermons), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons", methods=["POST"])
def create_sermon():
    payload = {
        "title": request.json.get("title"),
        "speaker_or_leader": request.json.get("speaker_or_leader"),
        "date": request.json.get("date"),
        "description": request.json.get("description"),
        "media_url": request.json.get("media_url")  # YouTube or other link
    }

    try:
        r = requests.post(f"{SUPABASE_URL}/sermons", headers=HEADERS, json=payload)
        r.raise_for_status()
        return jsonify(Sermon(r.json()).to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Health Check
# -----------------------------
@app.route("/health")
def health():
    return "OK", 200

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
