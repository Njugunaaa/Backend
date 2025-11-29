# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# -----------------------------
# Supabase Config
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
UPLOAD_BUCKET = "uploads"

# -----------------------------
# Helper functions
# -----------------------------
def upload_file_to_supabase(file, bucket=UPLOAD_BUCKET):
    try:
        filename = file.filename
        file_content = file.read()
        res = supabase.storage.from_(bucket).upload(filename, file_content, {"upsert": True})
        if res.get("error"):
            raise Exception(res["error"]["message"])
        public_url = supabase.storage.from_(bucket).get_public_url(filename)
        return public_url
    except Exception as e:
        raise Exception(f"File upload failed: {str(e)}")

def get_all(table):
    res = supabase.table(table).select("*").execute()
    if res.error:
        raise Exception(res.error.message)
    return res.data or []

def insert_one(table, payload):
    res = supabase.table(table).insert(payload).execute()
    if res.error:
        raise Exception(res.error.message)
    return res.data

def update_one(table, record_id, payload):
    res = supabase.table(table).update(payload).eq("id", record_id).execute()
    if res.error:
        raise Exception(res.error.message)
    return res.data

def delete_one(table, record_id):
    res = supabase.table(table).delete().eq("id", record_id).execute()
    if res.error:
        raise Exception(res.error.message)
    return {"deleted": True}

# -----------------------------
# Routes: Events
# -----------------------------
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        return jsonify(get_all("events")), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events", methods=["POST"])
def create_event():
    try:
        file = request.files.get("image")
        image_url = upload_file_to_supabase(file) if file else ""

        payload = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description", ""),
            "date": request.form.get("date", ""),
            "time": request.form.get("time", ""),
            "location": request.form.get("location", ""),
            "category": request.form.get("category", ""),
            "image_path": image_url
        }
        return jsonify(insert_one("events", [payload])), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events/<int:event_id>", methods=["PUT", "PATCH"])
def update_event(event_id):
    try:
        file = request.files.get("image")
        image_url = upload_file_to_supabase(file) if file else request.form.get("image_path", "")

        payload = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description", ""),
            "date": request.form.get("date", ""),
            "time": request.form.get("time", ""),
            "location": request.form.get("location", ""),
            "category": request.form.get("category", ""),
            "image_path": image_url
        }
        return jsonify(update_one("events", event_id, payload)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        return jsonify(delete_one("events", event_id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Routes: Sermons
# -----------------------------
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    try:
        return jsonify(get_all("sermons")), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons", methods=["POST"])
def create_sermon():
    try:
        payload = {
            "title": request.json.get("title", ""),
            "speaker_or_leader": request.json.get("speaker_or_leader", ""),
            "date": request.json.get("date", ""),
            "description": request.json.get("description", ""),
            "media_url": request.json.get("media_url", "")
        }
        return jsonify(insert_one("sermons", [payload])), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons/<int:sermon_id>", methods=["PUT", "PATCH"])
def update_sermon(sermon_id):
    try:
        payload = {
            "title": request.json.get("title", ""),
            "speaker_or_leader": request.json.get("speaker_or_leader", ""),
            "date": request.json.get("date", ""),
            "description": request.json.get("description", ""),
            "media_url": request.json.get("media_url", "")
        }
        return jsonify(update_one("sermons", sermon_id, payload)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons/<int:sermon_id>", methods=["DELETE"])
def delete_sermon(sermon_id):
    try:
        return jsonify(delete_one("sermons", sermon_id)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Health check
# -----------------------------
@app.route("/health")
def health():
    return "OK", 200

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
