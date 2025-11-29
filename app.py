from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from werkzeug.utils import secure_filename
from supabase import create_client, Client
import os
from models import Event, Sermon
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------------------
# Supabase Setup
# ---------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = "Elim@2025"


def admin_only(req):
    pw = req.headers.get("X-ADMIN-PASSWORD", "")
    return pw == ADMIN_PASSWORD


# ---------------------------
# Upload Helper
# ---------------------------
def upload_to_bucket(file):
    filename = secure_filename(file.filename)
    ext = filename.split(".")[-1]

    new_name = f"{uuid.uuid4()}.{ext}"
    file_path = f"events/{new_name}"  # Folder inside the bucket

    # Upload
    upload = supabase.storage.from_("uploads").upload(
        file_path,
        file,
        {"content-type": file.mimetype}
    )

    # Generate public URL
    public_url = supabase.storage.from_("uploads").get_public_url(file_path)
    return public_url


# ======================================================
# EVENTS ROUTES
# ======================================================

@app.route("/api/events", methods=["GET"])
def get_events():
    res = supabase.table("events").select("*").execute()
    if res.data is None:
        return jsonify([]), 200

    events = [Event(row).to_dict() for row in res.data]
    return jsonify(events), 200


@app.route("/api/events", methods=["POST"])
def create_event():
    if not admin_only(request):
        return jsonify({"error": "Unauthorized"}), 401

    title = request.form.get("title", "")
    description = request.form.get("description", "")
    date = request.form.get("date", "")
    time = request.form.get("time", "")
    location = request.form.get("location", "")
    category = request.form.get("category", "")

    image_url = None
    if "image" in request.files:
        image_url = upload_to_bucket(request.files["image"])

    payload = {
        "title": title,
        "description": description,
        "date": date,
        "time": time,
        "location": location,
        "category": category,
        "image_url": image_url,   # MUST MATCH SUPABASE COLUMN
    }

    res = supabase.table("events").insert(payload).execute()

    if res.data:
        return jsonify(res.data[0]), 201

    return jsonify({"error": "Failed to save event"}), 400


@app.route("/api/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    if not admin_only(request):
        return jsonify({"error": "Unauthorized"}), 401

    updates = {}

    for key in ["title", "description", "date", "time", "location", "category"]:
        val = request.form.get(key)
        if val is not None:
            updates[key] = val

    if "image" in request.files:
        updates["image_url"] = upload_to_bucket(request.files["image"])

    res = supabase.table("events").update(updates).eq("id", event_id).execute()

    if res.data:
        return jsonify(res.data[0]), 200

    return jsonify({"error": "Failed to update event"}), 400


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    if not admin_only(request):
        return jsonify({"error": "Unauthorized"}), 401

    res = supabase.table("events").delete().eq("id", event_id).execute()
    return jsonify({"message": "Deleted"}), 200


# ======================================================
# SERMONS ROUTES (UNCHANGED)
# ======================================================

@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    res = supabase.table("sermons").select("*").execute()
    sermons = [Sermon(row).to_dict() for row in res.data]
    return jsonify(sermons), 200


@app.route("/api/sermons", methods=["POST"])
def create_sermon():
    if not admin_only(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    payload = {
        "title": data.get("title", ""),
        "speaker_or_leader": data.get("speaker_or_leader", ""),
        "description": data.get("description", ""),
        "media_url": data.get("media_url", ""),
        "date": data.get("date", "")
    }

    res = supabase.table("sermons").insert(payload).execute()
    if res.data:
        return jsonify(res.data[0]), 201

    return jsonify({"error": "Failed to save sermon"}), 400


@app.route("/api/sermons/<int:sid>", methods=["PATCH"])
def update_sermon(sid):
    if not admin_only(request):
        return jsonify({"error": "Unauthorized"}), 401

    updates = request.json or {}
    res = supabase.table("sermons").update(updates).eq("id", sid).execute()

    if res.data:
        return jsonify(res.data[0]), 200

    return jsonify({"error": "Failed to update sermon"}), 400


@app.route("/api/sermons/<int:sid>", methods=["DELETE"])
def delete_sermon(sid):
    if not admin_only(request):
        return jsonify({"error": "Unauthorized"}), 401

    supabase.table("sermons").delete().eq("id", sid).execute()
    return jsonify({"message": "Deleted"}), 200


@app.route("/")
def home():
    return jsonify({"message": "Backend running"}), 200


if __name__ == "__main__":
    app.run(debug=True)

