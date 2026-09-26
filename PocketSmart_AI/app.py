import os
from flask import Flask, jsonify, render_template, request
from gemini_utils import (
    get_home_recommendations,
    get_jewelry_recommendations,
    get_party_recommendations,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def home():
  return render_template("index.html")


# 1. Home Planner Endpoint
@app.route("/api/home", methods=["POST"])
def plan_home():
  data = request.get_json() or {}
  budget = float(data.get("budget", 10000))
  room_type = data.get("room_type", "Living Room")
  items = data.get("items", {})

  result = get_home_recommendations(budget, room_type, items)
  return jsonify(result)


# 2. Party Planner Endpoint
@app.route("/api/party", methods=["POST"])
def plan_party():
  data = request.get_json() or {}
  budget = float(data.get("budget", 20000))
  event_type = data.get("event_type", "Birthday")
  guest_count = int(data.get("guest_count", 20))
  venue_details = data.get("venue_details", "Home / Small Hall")

  result = get_party_recommendations(
      budget, event_type, guest_count, venue_details
  )
  return jsonify(result)


# 3. Jewelry Planner Endpoint (Supports Multipart Form Data with Image)
@app.route("/api/jewelry", methods=["POST"])
def plan_jewelry():
  budget = float(request.form.get("budget", 5000))
  occasion = request.form.get("occasion", "Wedding")
  style_pref = request.form.get("style_pref", "Ethnic Traditional")

  image_path = None
  if "image" in request.files:
    file = request.files["image"]
    if file.filename != "":
      filename = secure_filename(file.filename)
      image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
      file.save(image_path)

  result = get_jewelry_recommendations(
      budget, occasion, style_pref, image_path
  )
  return jsonify(result)


if __name__ == "__main__":
  app.run(debug=True, port=5000)