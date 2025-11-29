# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from supabase import create_client

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# -----------------------------
# Supabase Config
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # service_role key
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Helper functions
# -----------------------------
def upload_file_to_supabase(file, bucket="uploads"):
    filename = file.filename
    file_content = file.read()
    res = supabase.storage.from_(bucket).upload(filename, file_content, {"upsert": True})
    if res.get("error"):
        raise Exception(f"Upload failed: {res['error']['message']}")
    public_url = supabase.storage.from_(bucket).get_public_url(filename)
    return public_url

def supabase_get(table):
    res = supabase.table(table).select("*").execute()
    if res.get("error"):
        raise Exception(res["error"]["message"])
    return res["data"]

def supabase_post(table, payload):
    res = supabase.table(table).insert(payload).execute()
    if res.get("error"):
        raise Exception(res["error"]["message"])
    return res["data"]

def supabase_patch(table, record_id, payload):
    res = supabase.table(table).update(payload).eq("id", record_id).execute()
    if res.get("error"):
        raise Exception(res["error"]["message"])
    return res["data"]

def supabase_delete(table, record_id):
    res = supabase.table(table).delete().eq("id", record_id).execute()
    if res.get("error"):
        raise Exception(res["error"]["message"])
    return {"deleted": True}

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
        return jsonify(supabase_post("events", [payload])), 201
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
        return jsonify(supabase_post("sermons", [payload])), 201
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
