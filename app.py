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
# Helper function
# -----------------------------
def safe_execute(res):
    """
    Checks Supabase APIResponse for errors and returns the data.
    """
    if res.status_code >= 400:
        # Try to get error message
        msg = res.json().get("message") if hasattr(res, "json") else "Unknown Supabase error"
        raise Exception(msg)
    return res.data or []

# Upload file to Supabase Storage
def upload_file_to_supabase(file, bucket="uploads"):
    filename = file.filename
    file_content = file.read()
    res = supabase.storage.from_(bucket).upload(filename, file_content, {"upsert": True})
    if res.get("error"):
        raise Exception(res["error"]["message"])
    public_url = supabase.storage.from_(bucket).get_public_url(filename).get("publicURL")
    return public_url

# -----------------------------
# Routes: Events
# -----------------------------
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        res = supabase.table("events").select("*").execute()
        data = safe_execute(res)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events", methods=["POST"])
def create_event():
    try:
        file = request.files.get("image")
        image_url = upload_file_to_supabase(file) if file else None

        payload = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description", ""),
            "date": request.form.get("date", ""),
            "time": request.form.get("time", ""),
            "location": request.form.get("location", ""),
            "category": request.form.get("category", ""),
            "image_path": image_url or ""
        }

        res = supabase.table("events").insert(payload).execute()
        data = safe_execute(res)
        return jsonify(data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    try:
        file = request.files.get("image")
        image_url = upload_file_to_supabase(file) if file else None

        payload = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description", ""),
            "date": request.form.get("date", ""),
            "time": request.form.get("time", ""),
            "location": request.form.get("location", ""),
            "category": request.form.get("category", ""),
        }
        if image_url:
            payload["image_path"] = image_url

        res = supabase.table("events").update(payload).eq("id", event_id).execute()
        data = safe_execute(res)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        res = supabase.table("events").delete().eq("id", event_id).execute()
        safe_execute(res)
        return jsonify({"deleted": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Routes: Sermons
# -----------------------------
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    try:
        res = supabase.table("sermons").select("*").execute()
        data = safe_execute(res)
        return jsonify(data), 200
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
        res = supabase.table("sermons").insert(payload).execute()
        data = safe_execute(res)
        return jsonify(data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons/<int:sermon_id>", methods=["PATCH"])
def update_sermon(sermon_id):
    try:
        payload = {
            "title": request.json.get("title", ""),
            "speaker_or_leader": request.json.get("speaker_or_leader", ""),
            "date": request.json.get("date", ""),
            "description": request.json.get("description", ""),
            "media_url": request.json.get("media_url", "")
        }
        res = supabase.table("sermons").update(payload).eq("id", sermon_id).execute()
        data = safe_execute(res)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sermons/<int:sermon_id>", methods=["DELETE"])
def delete_sermon(sermon_id):
    try:
        res = supabase.table("sermons").delete().eq("id", sermon_id).execute()
        safe_execute(res)
        return jsonify({"deleted": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Health check
# -----------------------------
@app.route("/health")
def health():
    return "OK", 200

# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
