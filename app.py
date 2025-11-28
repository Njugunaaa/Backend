from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# -----------------------------
# 🔗 Supabase REST API Config
# -----------------------------
SUPABASE_URL = "https://qkwkheukgubkqqccyzpu.supabase.co/rest/v1"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Add this in Render dashboard
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# -----------------------------
# Health Check
# -----------------------------
@app.route('/health')
def health():
    return 'OK', 200

# -----------------------------
# Events Endpoints
# -----------------------------
@app.route("/api/events", methods=["GET"])
def get_events():
    resp = requests.get(f"{SUPABASE_URL}/events", headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/api/events", methods=["POST"])
def add_event():
    data = request.get_json()
    resp = requests.post(f"{SUPABASE_URL}/events", json=data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/api/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    data = request.get_json()
    resp = requests.patch(f"{SUPABASE_URL}/events?id=eq.{event_id}", json=data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    resp = requests.delete(f"{SUPABASE_URL}/events?id=eq.{event_id}", headers=HEADERS)
    return jsonify({"status": "deleted"}), resp.status_code

# -----------------------------
# Sermons Endpoints
# -----------------------------
@app.route("/api/sermons", methods=["GET"])
def get_sermons():
    resp = requests.get(f"{SUPABASE_URL}/sermons", headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/api/sermons", methods=["POST"])
def add_sermon():
    data = request.get_json()
    resp = requests.post(f"{SUPABASE_URL}/sermons", json=data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/api/sermons/<int:sermon_id>", methods=["PATCH"])
def update_sermon(sermon_id):
    data = request.get_json()
    resp = requests.patch(f"{SUPABASE_URL}/sermons?id=eq.{sermon_id}", json=data, headers=HEADERS)
    return jsonify(resp.json()), resp.status_code

@app.route("/api/sermons/<int:sermon_id>", methods=["DELETE"])
def delete_sermon(sermon_id):
    resp = requests.delete(f"{SUPABASE_URL}/sermons?id=eq.{sermon_id}", headers=HEADERS)
    return jsonify({"status": "deleted"}), resp.status_code

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
