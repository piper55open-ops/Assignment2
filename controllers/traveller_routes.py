from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
import os, json, re, requests
import uuid
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from models.database import Database
from models.trip_model import TripModel
from models.user_model import UserModel
from models.feedback_model import FeedbackModel
from werkzeug.utils import secure_filename
from models.database import Database

traveller_bp = Blueprint("traveller", __name__, url_prefix="/traveller")
trip_model = TripModel()
User = UserModel()
feedback_model = FeedbackModel()

# --- Load NZ locations ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOCATIONS_FILE = os.path.join(BASE_DIR, "..", "data", "locations.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

load_dotenv()  # 🔹 loads .env file into environment

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



with open(LOCATIONS_FILE, 'r') as f:
    NZ_LOCATIONS = json.load(f)


# Inside traveller_routes.py (or wherever your blueprint is defined)
@traveller_bp.context_processor
def inject_traveller_user():
    traveller_id = session.get("user_id")
    traveller = None
    if traveller_id and session.get("role") == "tourist":

        user_model = UserModel()
        traveller = user_model.get_user_by_id(traveller_id)
    return dict(current_traveller=traveller)

@traveller_bp.route("/dashboard")
def traveller_dashboard():
    """Traveller main dashboard"""
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access. Please log in as a traveller.", "danger")
        return redirect(url_for("login"))

    db = Database()
  
    user_id = session.get("user_id")

    traveller = db.fetchone("SELECT * FROM users WHERE id=?", (user_id,))
    if not traveller:
        flash("Traveller profile not found.", "warning")
        return redirect(url_for("login"))

    traveller_name = traveller["username"]

    # 🗓 Detect current NZ season
    month = datetime.now().month
    if month in [12, 1, 2]:
        season = "Summer"
        keywords = ["beach holidays", "island trips", "coastal destinations"]
    elif month in [3, 4, 5]:
        season = "Autumn"
        keywords = ["autumn walks", "vineyard tours", "forest retreats"]
    elif month in [6, 7, 8]:
        season = "Winter"
        keywords = ["ski resorts", "hot springs", "mountain adventures"]
    else:  # [9, 10, 11]
        season = "Spring"
        keywords = ["botanical gardens", "flower festivals", "hiking trails"]

    # 🌍 Fetch seasonal recommendations dynamically from Google Places API
    seasonal_places = []
    for keyword in keywords:
        url = (
            f"https://maps.googleapis.com/maps/api/place/textsearch/json"
            f"?query={keyword}+in+New+Zealand&key={GOOGLE_API_KEY}"
        )
        res = requests.get(url).json()

        # Take top 2 per keyword
        for place in res.get("results", [])[:2]:
            photo_ref = place.get("photos", [{}])[0].get("photo_reference")
            image_url = (
                f"https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=600&photo_reference={photo_ref}&key={GOOGLE_API_KEY}"
                if photo_ref else "https://via.placeholder.com/600x400?text=No+Image"
            )
            seasonal_places.append({
                "name": place["name"],
                "description": place.get("formatted_address", "Beautiful New Zealand destination."),
                "image": image_url,
                "link": f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}"
            })

    # 🧳 Trip summary
    trips = trip_model.get_trips_by_user(user_id)
    total_trips = len(trips)

    return render_template(
        "traveller/traveller_dashboard.html",
        traveller=traveller,
        traveller_name=traveller_name,
        total_trips=total_trips,
        seasonal_places=seasonal_places,
        current_season=season
    )
    
def get_ai_itinerary(destination, nights, budget, adults, children, preferences):
    """
    Generate itinerary using OpenAI GPT model.
    """
    prompt = f"""
    Plan a {nights}-day trip to {destination} for {adults} adults and {children} children.
    Budget: ${budget}.
    Preferences: {', '.join(preferences)}.
    Include day-by-day plan with Morning, Afternoon, Evening, Night activities,
    with approximate costs and restaurant/hotel suggestions.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a travel planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI itinerary generation error:", e)
        return "Error generating itinerary. Please try again."
    

def parse_itinerary_to_structure(itinerary_text):
    """
    Convert AI-generated itinerary text into structured format
    [
      {
        "day": 1,
        "schedule": [
            {"time": "Morning", "text": "..."},
            {"time": "Afternoon", "text": "..."},
        ]
      },
      ...
    ]
    """
    if not itinerary_text:
        return []

    # Split days cleanly
    day_sections = re.split(r"(?i)\bDay\s+\d+\b", itinerary_text)
    day_numbers = re.findall(r"(?i)\bDay\s+(\d+)\b", itinerary_text)
    structured = []

    for i, content in enumerate(day_sections[1:], start=0):
        day_data = {"day": int(day_numbers[i]), "schedule": []}
        
        # Capture each time section (morning, afternoon, etc.)
        for time in ["Morning", "Afternoon", "Evening", "Night"]:
            pattern = rf"(?i){time}:(.*?)(?=(Morning|Afternoon|Evening|Night|$))"
            match = re.search(pattern, content, re.S)
            if match:
                text = match.group(1).strip()
                # Clean up bullet points
                text = re.sub(r"(\r?\n)+", "\n", text).strip()

                icon = {
                    "Morning": "☀️",
                    "Afternoon": "🌇",
                    "Evening": "🌆",
                    "Night": "🌙"
                }[time]

                day_data["schedule"].append({
                    "time": time,
                    "icon": icon,
                    "text": text
                })

        structured.append(day_data)

    return structured



@traveller_bp.route("/ai_planner", methods=["GET", "POST"])
def ai_planner():
    user_id = session.get("user_id")  # get logged-in user id
    traveller = None
    if user_id:
        traveller = User.get_user_by_id(user_id)  # only if you have this method
    else:
        traveller = {"username": "Guest"}

    itinerary = None
    structured_itinerary = None
    day_sections = None

    if request.method == "POST":
        destination = request.form.get("destination")
        nights = int(request.form.get("nights"))
        budget = request.form.get("budget") or "Flexible"
        adults = request.form.get("adults")
        children = request.form.get("children")
        preferences = request.form.getlist("preferences")

        itinerary = get_ai_itinerary(destination, nights, budget, adults, children, preferences)
        structured_itinerary = parse_itinerary_to_structure(itinerary)

    return render_template(
        "traveller/trip_planner.html",
        current_traveller=traveller,
        itinerary=itinerary,
        itinerary_data=structured_itinerary,
        raw_itinerary=itinerary,
        day_sections=[]
    )


def get_nearby_accommodations(destination, radius=5000):
    """
    Fetch nearby hotels or stays using Google Places API.
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"hotels in {destination}",
        "radius": radius,
        "key": GOOGLE_API_KEY
    }

    res = requests.get(url, params=params)
    data = res.json()
    accommodations = []

    for place in data.get("results", []):
        accommodations.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating"),
            "location": place.get("geometry", {}).get("location")
        })

    return accommodations

@traveller_bp.route("/memories", methods=["GET", "POST"])
def memories():
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    traveller = User.get_user_by_id(user_id)
    
    if request.method == "POST":
        title = request.form["title"]
        story = request.form["story"]
        date = request.form["date"]
        image = request.files["image"]

        if image and image.filename != "":
            filename = image.filename
            upload_folder = os.path.join("static", "images")

            os.makedirs(upload_folder, exist_ok=True)

            upload_path = os.path.join(upload_folder, filename)
            image.save(upload_path)

            # Store in DB (update this part according to your DB helper)
            db =  Database()  # replace with your actual db instance
            db.execute(
                "INSERT INTO travel_memories (user_id, title, story, date, image) VALUES (?, ?, ?, ?, ?)",
                (session["user_id"], title, story, date, filename),
            )
            flash("Memory added successfully!", "success")
            return redirect(url_for("traveller.memories"))

    # Retrieve all memories for this user
    db =  Database()  # replace with your actual db instance
    memories = db.execute(
        "SELECT * FROM travel_memories WHERE user_id = ?", (session["user_id"],)
    ).fetchall()

    return render_template("traveller/traveller_memories.html", memories=memories,current_traveller=traveller)

@traveller_bp.route("/nearby_stays")
def nearby_stays():
    """Render the Nearby Stays page."""
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    traveller = User.get_user_by_id(user_id)
    
    return render_template("traveller/nearby_stays.html", google_api_key=GOOGLE_API_KEY,current_traveller=traveller)


@traveller_bp.route("/get_nearby_hotels", methods=["POST"])
def get_nearby_hotels():
    """Fetch nearby hotels using Google Places API and Distance Matrix."""
    data = request.get_json()
    location = data.get("location")  # { "lat": ..., "lng": ... }

    if not location:
        return jsonify({"error": "Location not provided"}), 400

    # Google Places Nearby Search API
    places_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={location['lat']},{location['lng']}"
        f"&radius=3000&type=lodging&key={GOOGLE_API_KEY}"
    )
    places_response = requests.get(places_url).json()

    hotels = []
    if "results" in places_response:
        for place in places_response["results"]:
            name = place.get("name")
            address = place.get("vicinity")
            rating = place.get("rating", "N/A")
            photo_ref = (
                place.get("photos", [{}])[0].get("photo_reference")
                if place.get("photos")
                else None
            )

            photo_url = (
                f"https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=400&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
                if photo_ref
                else "/static/images/noimage.jpg"
            )

            # Distance Matrix for duration
            dest_lat = place["geometry"]["location"]["lat"]
            dest_lng = place["geometry"]["location"]["lng"]

            dist_url = (
                f"https://maps.googleapis.com/maps/api/distancematrix/json?"
                f"origins={location['lat']},{location['lng']}&"
                f"destinations={dest_lat},{dest_lng}&key={GOOGLE_API_KEY}"
            )

            dist_data = requests.get(dist_url).json()
            distance = "N/A"
            duration = "N/A"
            if (
                "rows" in dist_data
                and dist_data["rows"][0]["elements"][0]["status"] == "OK"
            ):
                distance = dist_data["rows"][0]["elements"][0]["distance"]["text"]
                duration = dist_data["rows"][0]["elements"][0]["duration"]["text"]

            hotels.append(
                {
                    "name": name,
                    "address": address,
                    "rating": rating,
                    "photo": photo_url,
                    "distance": distance,
                    "duration": duration,
                }
            )

    return jsonify(hotels)



@traveller_bp.route("/my-trips", methods=["GET", "POST"])
def traveller_trips():
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    traveller = User.get_user_by_id(user_id)
    
    if request.method == "POST":
        title = request.form.get("title")
        destination = request.form.get("destination")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        budget = request.form.get("budget")
        description = request.form.get("description")
        status = request.form.get("status")
        google_maps_url = request.form.get("google_maps_url")
        cover_image_file = request.files.get("cover_image")
        cover_image_filename = None

        if cover_image_file and cover_image_file.filename != "":
            cover_image_filename = secure_filename(cover_image_file.filename)
            cover_image_path = os.path.join(UPLOAD_FOLDER, cover_image_filename)
            cover_image_file.save(cover_image_path)

        trip_model.add_trip(
            user_id=user_id,
            title=title,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            description=description,
            status=status,
            cover_image=cover_image_filename,
            google_maps_url=google_maps_url
        )
        flash("Trip added successfully!", "success")
        return redirect(url_for("traveller.memories"))

    # Fetch all trips for this user
    trips = trip_model.get_trips_by_user(user_id)
    return render_template("traveller/traveller_trips.html", trips=trips,current_traveller=traveller)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@traveller_bp.route('/profile', methods=['GET'])
def profile():
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    traveller = User.get_user_by_id(session.get('user_id'))
    user_id = session.get("user_id")
    return render_template('traveller/traveller_profile.html', traveller=traveller)


@traveller_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get('user_id')
    username = request.form['username']
    email = request.form['email']

    image = None
    if 'image' in request.files and request.files['image'].filename != '':
        img_file = request.files['image']
        filename = img_file.filename
        path = os.path.join(UPLOAD_FOLDER, filename)
        img_file.save(path)
        image = filename

    User.update_profile(user_id, username, email, image)
    flash("Profile updated successfully!", "success")
    return redirect(url_for("traveller_bp.profile"))



# ✅ Page Load Route
@traveller_bp.route("/traveller/feedback", methods=["GET"])
def traveller_feedback_page():
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    traveller = User.get_user_by_id(user_id)
    feedbacks = feedback_model.get_feedbacks_by_user(user_id, "tourist")
    unread_count = feedback_model.get_unread_replies_count(user_id, "tourist")

    # Optional messages for SweetAlert
    success_message = request.args.get("success")
    error_message = request.args.get("error")

    return render_template(
        "traveller/feedback_notifications.html",
        feedbacks=feedbacks,
        traveller=traveller,
        unread_count=unread_count,
        success_message=success_message,
        error_message=error_message
    )


# ✅ Normal POST Route (no AJAX)
@traveller_bp.route("/traveller/feedback/send", methods=["POST"])
def traveller_send_feedback():
    if "role" not in session or session["role"] != "tourist":
        return redirect(url_for("traveller.traveller_feedback_page", error="Unauthorized access"))

    try:
        user_id = session.get("user_id")
        traveller = User.get_user_by_id(user_id)
        traveller_name = traveller["username"]
        traveller_email = traveller["email"]

        message = request.form.get("message")
        if not message:
            return redirect(url_for("traveller.traveller_feedback_page", error="Message cannot be empty"))

        feedback_model.add_feedback(user_id, "tourist", traveller_name, traveller_email, message)
        return redirect(url_for("traveller.traveller_feedback_page", success="Feedback submitted successfully!"))

    except Exception as e:
        print("Feedback submission error:", e)
        return redirect(url_for("traveller.traveller_feedback_page", error="Server error occurred"))
