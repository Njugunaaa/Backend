import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ------------------------------------
# Supabase Config
# ------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

REST_URL = f"{SUPABASE_URL}/rest/v1"
STORAGE_URL = f"{SUPABASE_URL}/storage/v1/object"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ------------------------------------
# Upload to Supabase Storage
# ------------------------------------
def upload_image(file):
    if not file:
        return None

    filename = file.filename
    file_bytes = file.read()

    upload_path = f"churchbucket/{filename}"

    r = requests.post(
        f"{STORAGE_URL}/{upload_path}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/octet-stream"
        },
        data=file_bytes
    )

    if r.status_code not in [200, 201]:
        print("UPLOAD ERROR:", r.text)
        return None

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/churchbucket/{filename}"
    return public_url


# ------------------------------------
# EVENTS CRUD
# ------------------------------------
@app.route("/api/events", methods=["GET"])
def get_events():
    r = requests.get(f"{REST_URL}/events", headers=HEADERS)
    return jsonify(r.json()), 200

@app.route("/api/events", methods=["POST"])
def create_event():
    image = upload_image(request.files.get("image"))

    payload = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "date": request.form.get("date"),
        "time": request.form.get("time"),
        "location": request.form.get("location"),
        "category": request.form.get("category"),
        "image_path": image
    }

    r = requests.post(f"{REST_URL}/events", headers=HEADERS, json=payload)
    return jsonify(r.json()), 201

@app.route("/api/events/<id>", methods=["DELETE"])
def delete_event(id):
    r = requests.delete(f"{REST_URL}/events?id=eq.{id}", headers=HEADERS)
    return jsonify({"message": "Deleted"}), 200


# ------------------------------------
# SERMONS CRUD
# ------------------------------------
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    r = requests.get(f"{REST_URL}/sermons", headers=HEADERS)
    return jsonify(r.json()), 200

@app.route("/api/sermons", methods=["POST"])
def create_sermon():
    image = upload_image(request.files.get("image"))

    payload = {
        "title": request.form.get("title"),
        "speaker_or_leader": request.form.get("speaker_or_leader"),
        "date": request.form.get("date"),
        "description": request.form.get("description"),
        "media_url": request.form.get("media_url"),
        "image_path": image
    }

    r = requests.post(f"{REST_URL}/sermons", headers=HEADERS, json=payload)
    return jsonify(r.json()), 201

@app.route("/api/sermons/<id>", methods=["DELETE"])
def delete_sermon(id):
    r = requests.delete(f"{REST_URL}/sermons?id=eq.{id}", headers=HEADERS)
    return jsonify({"message": "Deleted"}), 200


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    app.run(debug=True)
