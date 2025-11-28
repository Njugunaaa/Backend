# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Event, Sermon
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---------------------------------------
# Supabase REST Config
# ---------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")  # e.g. https://xyz.supabase.co/rest/v1
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # service role key

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ---------------------------------------
# Upload folder
# ---------------------------------------
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# 🟦 EVENTS CRUD
# ============================================================

# GET ALL EVENTS
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        r = requests.get(f"{SUPABASE_URL}/events", headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        return jsonify([Event(e).to_dict() for e in data]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET SINGLE EVENT
@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    try:
        url = f"{SUPABASE_URL}/events?id=eq.{event_id}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        rows = r.json()
        if not rows:
            return jsonify({"error": "Event not found"}), 404
        return jsonify(Event(rows[0]).to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# CREATE EVENT
@app.route("/api/events", methods=["POST"])
def create_event():
    try:
        file = request.files.get("image")
        image_url = None

        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            image_url = f"/static/uploads/{filename}"

        payload = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "image_path": image_url,
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "location": request.form.get("location"),
            "category": request.form.get("category")
        }

        r = requests.post(f"{SUPABASE_URL}/events", headers=HEADERS, json=payload)
        r.raise_for_status()

        return jsonify(Event(r.json()).to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UPDATE EVENT
@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    try:
        payload = request.json

        url = f"{SUPABASE_URL}/events?id=eq.{event_id}"
        r = requests.patch(url, headers=HEADERS, json=payload)
        r.raise_for_status()

        updated = r.json()
        if not updated:
            return jsonify({"error": "Event not found"}), 404

        return jsonify(Event(updated[0]).to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DELETE EVENT
@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        url = f"{SUPABASE_URL}/events?id=eq.{event_id}"
        r = requests.delete(url, headers=HEADERS)
        r.raise_for_status()
        return jsonify({"message": "Event deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# 🟩 SERMONS CRUD
# ============================================================

# GET ALL SERMONS
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    try:
        r = requests.get(f"{SUPABASE_URL}/sermons", headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        return jsonify([Sermon(s).to_dict() for s in data]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET SINGLE SERMON
@app.route("/api/sermons/<int:sermon_id>", methods=["GET"])
def get_sermon(sermon_id):
    try:
        url = f"{SUPABASE_URL}/sermons?id=eq.{sermon_id}"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()

        rows = r.json()
        if not rows:
            return jsonify({"error": "Sermon not found"}), 404

        return jsonify(Sermon(rows[0]).to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# CREATE SERMON
@app.route("/api/sermons", methods=["POST"])
def create_sermon():
    try:
        payload = request.json

        r = requests.post(f"{SUPABASE_URL}/sermons", headers=HEADERS, json=payload)
        r.raise_for_status()

        return jsonify(Sermon(r.json()).to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# UPDATE SERMON
@app.route("/api/sermons/<int:sermon_id>", methods=["PUT"])
def update_sermon(sermon_id):
    try:
        payload = request.json

        url = f"{SUPABASE_URL}/sermons?id=eq.{sermon_id}"
        r = requests.patch(url, headers=HEADERS, json=payload)
        r.raise_for_status()

        updated = r.json()
        if not updated:
            return jsonify({"error": "Sermon not found"}), 404

        return jsonify(Sermon(updated[0]).to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# DELETE SERMON
@app.route("/api/sermons/<int:sermon_id>", methods=["DELETE"])
def delete_sermon(sermon_id):
    try:
        url = f"{SUPABASE_URL}/sermons?id=eq.{sermon_id}"
        r = requests.delete(url, headers=HEADERS)
        r.raise_for_status()
        return jsonify({"message": "Sermon deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------
# Health Check
# ------------------------------------------------
@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
