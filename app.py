from flask import Flask, request, jsonify
from flask_cors import CORS
from models import Event, Sermon
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---------------------------------------
# Supabase Config
# ---------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")  # MUST end with /rest/v1
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Service Role Key

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ---------------------------------------
# Upload folder (Event posters)
# ---------------------------------------
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------------------
# Helper – handles BOTH JSON + form-data
# ---------------------------------------
def get_json_or_form():
    if request.is_json:
        return request.get_json()
    else:
        return request.form.to_dict()

# =======================================
# EVENTS ROUTES
# =======================================

# Get all events
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        url = f"{SUPABASE_URL}/events?select=*"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        events = [Event(e).to_dict() for e in r.json()]
        return jsonify(events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Create event
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

        payload = get_json_or_form()
        payload["image_path"] = image_url

        url = f"{SUPABASE_URL}/events"
        r = requests.post(url, headers=HEADERS, json=payload)
        r.raise_for_status()

        created = r.json()
        return jsonify(created), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update event
@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    try:
        payload = get_json_or_form()

        url = f"{SUPABASE_URL}/events?id=eq.{event_id}"
        r = requests.patch(url, headers=HEADERS, json=payload)
        r.raise_for_status()

        updated = r.json()
        if not updated:
            return jsonify({"error": "Event not found"}), 404

        return jsonify(updated[0]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete event
@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        url = f"{SUPABASE_URL}/events?id=eq.{event_id}"
        r = requests.delete(url, headers=HEADERS)
        r.raise_for_status()
        return jsonify({"message": "Event deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =======================================
# SERMONS ROUTES
# =======================================

# Get all sermons
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    try:
        url = f"{SUPABASE_URL}/sermons?select=*"
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        sermons = [Sermon(s).to_dict() for s in r.json()]
        return jsonify(sermons), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Create sermon
@app.route("/api/sermons", methods=["POST"])
def create_sermon():
    try:
        payload = get_json_or_form()

        url = f"{SUPABASE_URL}/sermons"
        r = requests.post(url, headers=HEADERS, json=payload)
        r.raise_for_status()

        created = r.json()
        return jsonify(created), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update sermon
@app.route("/api/sermons/<int:sermon_id>", methods=["PUT"])
def update_sermon(sermon_id):
    try:
        payload = get_json_or_form()

        url = f"{SUPABASE_URL}/sermons?id=eq.{sermon_id}"
        r = requests.patch(url, headers=HEADERS, json=payload)
        r.raise_for_status()

        updated = r.json()
        if not updated:
            return jsonify({"error": "Sermon not found"}), 404

        return jsonify(updated[0]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete sermon
@app.route("/api/sermons/<int:sermon_id>", methods=["DELETE"])
def delete_sermon(sermon_id):
    try:
        url = f"{SUPABASE_URL}/sermons?id=eq.{sermon_id}"
        r = requests.delete(url, headers=HEADERS)
        r.raise_for_status()
        return jsonify({"message": "Sermon deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------
# Health Check
# ---------------------------------------
@app.route("/health")
def health():
    return "OK", 200


# ---------------------------------------
# Run app
# ---------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
