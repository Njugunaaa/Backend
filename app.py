import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------
#  SUPABASE CONFIG
# ---------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase environment variables NOT found.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------
#  HELPERS
# ---------------------------------------------------
def upload_to_bucket(file, folder="events"):
    """
    Uploads a file into Supabase storage and returns a public URL.
    Fixes the boolean->header bug by ensuring metadata is ALWAYS strings only.
    """
    try:
        filename = secure_filename(file.filename)
        ext = filename.split(".")[-1]
        new_name = f"{uuid.uuid4()}.{ext}"
        file_path = f"{folder}/{new_name}"

        # --- UPLOAD ---
        upload = supabase.storage.from_(folder).upload(
            file_path,
            file,
            {"content-type": file.mimetype}  # MUST be string-only dict values
        )

        if upload is None:
            return None

        # --- PUBLIC URL ---
        public_url = supabase.storage.from_(folder).get_public_url(file_path)
        return public_url

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return None


# ---------------------------------------------------
#  SERMONS ROUTES (working like your old good version)
# ---------------------------------------------------
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    try:
        data = supabase.table("sermons").select("*").order("created_at", desc=True).execute()
        return jsonify(data.data), 200
    except Exception as e:
        print("SERMONS ERROR:", e)
        return jsonify({"error": "Failed to fetch sermons"}), 500


@app.route("/api/sermons", methods=["POST"])
def add_sermon():
    try:
        body = request.json
        title = body.get("title")
        preacher = body.get("preacher")
        date = body.get("date")
        url = body.get("url")

        payload = {
            "title": title,
            "preacher": preacher,
            "date": date,
            "url": url,
        }

        result = supabase.table("sermons").insert(payload).execute()
        return jsonify(result.data), 201
    except Exception as e:
        print("ADD SERMON ERROR:", e)
        return jsonify({"error": "Failed to add sermon"}), 500


# ---------------------------------------------------
#  EVENTS ROUTES (FIXED)
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

        image_file = request.files.get("image")

        image_url = None
        if image_file:
            image_url = upload_to_bucket(image_file, folder="events")

        payload = {
            "title": title,
            "description": description,
            "date": date,
            "image_url": image_url,
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

        image_file = request.files.get("image")

        update_data = {
            "title": title,
            "description": description,
            "date": date,
        }

        if image_file:
            image_url = upload_to_bucket(image_file, folder="events")
            update_data["image_url"] = image_url

        result = supabase.table("events").update(update_data).eq("id", event_id).execute()
        return jsonify(result.data), 200

    except Exception as e:
        print("EVENT UPDATE ERROR:", e)
        return jsonify({"error": "Failed to update event"}), 500


# ---------------------------------------------------
#  DEBUG ROUTE (to confirm Flask runs)
# ---------------------------------------------------
@app.route("/api/test")
def test():
    return "Flask is running OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
