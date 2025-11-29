from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from supabase import create_client

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -----------------------------
# Helper Functions
# -----------------------------
def check_response(res):
    """Check Supabase APIResponse and raise Exception if there is an error"""
    if hasattr(res, "error") and res.error:
        raise Exception(str(res.error))
    return getattr(res, "data", []) or []


def upload_file_to_supabase(file, bucket="uploads"):
    """Upload file to Supabase storage and return public URL"""
    filename = file.filename
    content = file.read()
    res = supabase.storage.from_(bucket).upload(filename, content, {"upsert": True})
    if getattr(res, "error", None):
        raise Exception(str(res.error))
    public_url = supabase.storage.from_(bucket).get_public_url(filename).get("publicURL")
    return str(public_url)


# -----------------------------
# Events Routes
# -----------------------------
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        res = supabase.table("events").select("*").execute()
        data = check_response(res)
        return jsonify(data)
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

        res = supabase.table("events").insert(payload).execute()
        data = check_response(res)
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
        data = check_response(res)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        res = supabase.table("events").delete().eq("id", event_id).execute()
        check_response(res)
        return jsonify({"deleted": True})
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
