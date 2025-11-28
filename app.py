# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# -----------------------------
# Supabase Config
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")  # e.g. https://xyz.supabase.co
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Service role key
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object"

# -----------------------------
# Helper functions
# -----------------------------
def upload_file_to_supabase(file, bucket="uploads"):
    filename = file.filename
    tmp_path = os.path.join("/tmp", filename)
    file.save(tmp_path)
    url = f"{STORAGE_URL}/upload/{bucket}/{filename}"
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}"}
    with open(tmp_path, "rb") as f:
        res = requests.post(url, headers=headers, files={"file": f})
    if res.status_code != 200:
        raise Exception(f"Upload failed: {res.text}")
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"

def supabase_get(table):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS)
    r.raise_for_status()
    return r.json()

def supabase_post(table, payload):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

def supabase_patch(table, record_id, payload):
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{record_id}", headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

def supabase_delete(table, record_id):
    r = requests.delete(f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{record_id}", headers=HEADERS)
    r.raise_for_status()
    return r.json()

# -----------------------------
# Routes: Events
# -----------------------------
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        return jsonify(supabase_get("events")), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events", methods=["POST"])
def create_event():
    try:
        file = request.files.get("image")
        image_url = upload_file_to_supabase(file) if file else None

        payload = {
            "title": request.form.get("title") or "",
            "description": request.form.get("description") or "",
            "image_path": image_url or "",
            "date": request.form.get("date") or "",
            "time": request.form.get("time") or "",
            "location": request.form.get("location") or "",
            "category": request.form.get("category") or ""
        }
        return jsonify(supabase_post("events", payload)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    try:
        file = request.files.get("image")
        image_url = upload_file_to_supabase(file) if file else None

        payload = {
            "title": request.form.get("title") or "",
            "description": request.form.get("description") or "",
            "image_path": image_url if image_url else request.form.get("image_path"),
            "date": request.form.get("date") or "",
            "time": request.form.get("time") or "",
            "location": request.form.get("location") or "",
            "category": request.form.get("category") or ""
        }
        return jsonify(supabase_patch("events", event_id, payload)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        return jsonify(supabase_delete("events", event_id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Routes: Sermons
# -----------------------------
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    try:
        return jsonify(supabase_get("sermons")), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons", methods=["POST"])
def create_sermon():
    try:
        payload = {
            "title": request.json.get("title") or "",
            "speaker_or_leader": request.json.get("speaker_or_leader") or "",
            "date": request.json.get("date") or "",
            "description": request.json.get("description") or "",
            "media_url": request.json.get("media_url") or ""
        }
        return jsonify(supabase_post("sermons", payload)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons/<int:sermon_id>", methods=["PATCH"])
def update_sermon(sermon_id):
    try:
        payload = {
            "title": request.json.get("title") or "",
            "speaker_or_leader": request.json.get("speaker_or_leader") or "",
            "date": request.json.get("date") or "",
            "description": request.json.get("description") or "",
            "media_url": request.json.get("media_url") or ""
        }
        return jsonify(supabase_patch("sermons", sermon_id, payload)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons/<int:sermon_id>", methods=["DELETE"])
def delete_sermon(sermon_id):
    try:
        return jsonify(supabase_delete("sermons", sermon_id)), 200
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
