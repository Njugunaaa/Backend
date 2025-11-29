import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
# SUPABASE CONFIG
# ---------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase environment variables NOT found.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
def upload_to_bucket(file, bucket="uploads"):
    """Upload a file to Supabase storage and return its public URL."""
    try:
        if file is None:
            return None

        filename = secure_filename(file.filename)
        ext = filename.split(".")[-1]
        new_name = f"{uuid.uuid4()}.{ext}"

        # Supabase expects bytes
        file_bytes = file.read()

        # Upload to bucket
        res = supabase.storage.from_(bucket).upload(new_name, file_bytes, {"content-type": file.mimetype})
        if not res:
            print("Upload returned False")
            return None

        # Get public URL
        public_url = supabase.storage.from_(bucket).get_public_url(new_name)
        if isinstance(public_url, dict):
            return public_url.get("publicUrl")
        return public_url

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return None

# ---------------------------------------------------
# EVENTS ROUTES
# ---------------------------------------------------
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
        title = request.form.get("title")
        description = request.form.get("description")
        date = request.form.get("date")
        time_val = request.form.get("time")
        location = request.form.get("location")
        category = request.form.get("category")
        image_file = request.files.get("image")

        image_path = upload_to_bucket(image_file) if image_file else None

        payload = {
            "title": title,
            "description": description,
            "date": date,
            "time": time_val,
            "location": location,
            "category": category,
            "image_path": image_path
        }

        result = supabase.table("events").insert(payload).execute()
        return jsonify(result.data), 201

    except Exception as e:
        print("EVENT CREATE ERROR:", e)
        return jsonify({"error": "Failed to create event"}), 500

@app.route("/api/events/<int:event_id>", methods=["PUT", "PATCH"])
def update_event(event_id):
    try:
        title = request.form.get("title")
        description = request.form.get("description")
        date = request.form.get("date")
        time_val = request.form.get("time")
        location = request.form.get("location")
        category = request.form.get("category")
        image_file = request.files.get("image")

        update_data = {
            "title": title,
            "description": description,
            "date": date,
            "time": time_val,
            "location": location,
            "category": category,
        }
        if image_file:
            update_data["image_path"] = upload_to_bucket(image_file)

        result = supabase.table("events").update(update_data).eq("id", event_id).execute()
        return jsonify(result.data), 200

    except Exception as e:
        print("EVENT UPDATE ERROR:", e)
        return jsonify({"error": "Failed to update event"}), 500

# ---------------------------------------------------
# DEBUG ROUTE
# ---------------------------------------------------
@app.route("/api/test")
def test():
    return "Flask is running OK", 200

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
