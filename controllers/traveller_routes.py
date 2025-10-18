import datetime
from flask import Blueprint, render_template, session, redirect, url_for,json,flash,request,jsonify
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import openai
from models.database import Database
from models.trip_model import TripModel


traveller_bp = Blueprint("traveller", __name__, url_prefix="/traveller")


# --- Load NZ locations ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_FILE = os.path.join(BASE_DIR, "..", "data", "locations.json")


load_dotenv()  # 🔹 loads .env file into environment

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY


with open(LOCATIONS_FILE, 'r') as f:
    NZ_LOCATIONS = json.load(f)

@traveller_bp.route("/dashboard")
def traveller_dashboard():
    """Traveller main dashboard"""
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access. Please log in as a traveller.", "danger")
        return redirect(url_for("login"))

    db = Database()
    trip_model = TripModel()
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
        traveller_name=traveller_name,
        total_trips=total_trips,
        seasonal_places=seasonal_places,
        current_season=season
    )

@traveller_bp.route("/trip-planner", methods=["GET", "POST"])
def ai_planner():
    if "role" not in session or session["role"] != "tourist":
        flash("Unauthorized access. Please log in as a traveller.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.json
        destination = data.get("destination")
        nights = data.get("nights")
        adults = data.get("adults")
        children = data.get("children")
        budget = data.get("budget")
        preferences = data.get("preferences", [])
        selected_places = data.get("selected_places", [])

        prompt = f"""
        Create a {nights}-night travel itinerary for {adults} adults and {children} children in {destination}.
        Budget: ${budget}.
        Preferences: {', '.join(preferences)}.
        Must include these places: {', '.join(selected_places)}.
        Provide day-wise activities, suggested accommodations, dining, and local experiences in JSON format:
        [
          {{
            "day": 1,
            "activities": [
              {{
                "name": "Activity name",
                "time": "Morning/Afternoon/Evening",
                "location": "Place",
                "description": "Brief description",
                "image": "Image URL"
              }}
            ],
            "accommodation": "Hotel suggestion",
            "notes": "Any extra tips"
          }}
        ]
        """

        response =openai.ChatCompletion.create( # pylint: disable=no-member
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        itinerary_text = response.choices[0].message.content
        # Convert text to JSON safely
        
        try:
            itinerary = json.loads(itinerary_text)
        except:
            itinerary = {"error": "Failed to parse AI response", "raw": itinerary_text}

        return jsonify(itinerary)

    return render_template("traveller/trip_planner.html")

def generate_itinerary(destination, days, adults, children, budget):
    """
    Generate a travel itinerary using OpenAI.
    """
    system_prompt = "You are an expert travel planner."
    user_prompt = f"""
    Plan a {days}-day trip to {destination} for {adults} adults and {children} children.
    Include recommended activities, attractions, and budget-friendly options.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    itinerary = response.choices[0].message.content
    return itinerary
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

    
    
