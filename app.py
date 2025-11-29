import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app)

# ---------------- SUPABASE CONFIG ----------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase environment variables NOT found.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- HELPERS ----------------
def upload_to_bucket(file, bucket="uploads"):
    """
    Upload file to Supabase storage and return public URL.
    """
    try:
        filename = secure_filename(file.filename)
        ext = filename.split(".")[-1]
        new_name = f"{uuid.uuid4()}.{ext}"
        file_path = f"{new_name}"  # store directly in bucket

        # Upload the file
        supabase.storage.from_(bucket).upload(file_path, file, {"content-type": file.mimetype})

        # Get public URL
        public_url = supabase.storage.from_(bucket).get_public_url(file_path)
        return public_url
    except Exception as e:
        print("UPLOAD ERROR:", e)
        return None

# ---------------- EVENTS ROUTES ----------------
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        data = supabase.table("events").select("*").order("created_at", desc=True).execute()
        return jsonify(data.data), 200
    except Exception as e:
        print("EVENTS GET ERROR:", e)
        return jsonify({"error": "Failed to fetch events"}), 500

@app.route("/api/events", methods=["POST"])
def create_event():
    try:
        # Get form data
        title = request.form.get("title")
        description = request.form.get("description")
        date = request.form.get("date")
        time = request.form.get("time")
        location = request.form.get("location")
        category = request.form.get("category")

        # Handle file upload
        image_file = request.files.get("image")
        image_path = None
        if image_file:
            image_path = upload_to_bucket(image_file, bucket="uploads")

        # Insert into Supabase
        payload = {
            "title": title,
            "description": description,
            "date": date,
            "time": time,
            "location": location,
            "category": category,
            "image_path": image_path
        }
        result = supabase.table("events").insert(payload).execute()
        return jsonify(result.data), 201

    except Exception as e:
        print("EVENT CREATE ERROR:", e)
        return jsonify({"error": "Failed to create event"}), 500

@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    try:
        title = request.form.get("title")
        description = request.form.get("description")
        date = request.form.get("date")
        time = request.form.get("time")
        location = request.form.get("location")
        category = request.form.get("category")

        update_data = {
            "title": title,
            "description": description,
            "date": date,
            "time": time,
            "location": location,
            "category": category
        }

        image_file = request.files.get("image")
        if image_file:
            update_data["image_path"] = upload_to_bucket(image_file, bucket="uploads")

        result = supabase.table("events").update(update_data).eq("id", event_id).execute()
        return jsonify(result.data), 200

    except Exception as e:
        print("EVENT UPDATE ERROR:", e)
        return jsonify({"error": "Failed to update event"}), 500
