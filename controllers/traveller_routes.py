import datetime
from flask import Blueprint, render_template, session, redirect, url_for,json,flash
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
from models.database import Database
from models.trip_model import TripModel

traveller_bp = Blueprint("traveller", __name__, url_prefix="/traveller")


# --- Load NZ locations ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_FILE = os.path.join(BASE_DIR, "..", "data", "locations.json")


load_dotenv()  # 🔹 loads .env file into environment

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

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
# --------- HELPER FUNCTIONS ---------

def get_current_season(month: int):
    """Return the current season in New Zealand based on month."""
    if month in [12, 1, 2]:
        return "Summer"
    elif month in [3, 4, 5]:
        return "Autumn"
    elif month in [6, 7, 8]:
        return "Winter"
    else:
        return "Spring"

def get_seasonal_places(season: str):
    """Return sample seasonal recommendations."""
    if season == "Summer":
        return [
            {
                "name": "Bay of Islands",
                "description": "Enjoy crystal-clear beaches, sailing, and island-hopping adventures.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/3/33/Bay_of_Islands.jpg",
                "link": "https://www.newzealand.com/nz/bay-of-islands/"
            },
            {
                "name": "Abel Tasman National Park",
                "description": "Perfect for kayaking, golden sands, and summer hikes.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Abel_Tasman_National_Park.jpg",
                "link": "https://www.newzealand.com/nz/abel-tasman-national-park/"
            },
            {
                "name": "Coromandel Peninsula",
                "description": "Famous for its Hot Water Beach and scenic coastal drives.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Coromandel_Peninsula_Coast.jpg",
                "link": "https://www.newzealand.com/nz/coromandel/"
            }
        ]

    elif season == "Winter":
        return [
            {
                "name": "Queenstown",
                "description": "New Zealand’s winter capital for skiing and snowboarding.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/f/f2/Queenstown_winter.jpg",
                "link": "https://www.newzealand.com/nz/queenstown/"
            },
            {
                "name": "Mount Ruapehu",
                "description": "Hit the slopes or explore Tongariro National Park’s alpine beauty.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Mount_Ruapehu.jpg",
                "link": "https://www.newzealand.com/nz/tongariro-national-park/"
            },
            {
                "name": "Tekapo",
                "description": "Famous for stargazing and stunning winter landscapes.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Lake_Tekapo_Church_of_the_Good_Shepherd.jpg",
                "link": "https://www.newzealand.com/nz/lake-tekapo/"
            }
        ]

    elif season == "Autumn":
        return [
            {
                "name": "Arrowtown",
                "description": "Historic gold-mining village glowing with autumn colors.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Arrowtown_Autumn.jpg",
                "link": "https://www.newzealand.com/nz/arrowtown/"
            },
            {
                "name": "Hawke’s Bay",
                "description": "Vineyards and autumn festivals under mild weather.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/3/36/Hawkes_Bay_Vineyards.jpg",
                "link": "https://www.newzealand.com/nz/hawkes-bay/"
            }
        ]

    else:  # Spring
        return [
            {
                "name": "Christchurch Botanic Gardens",
                "description": "See tulips and cherry blossoms in full bloom.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Christchurch_Botanic_Gardens.jpg",
                "link": "https://www.newzealand.com/nz/christchurch/"
            },
            {
                "name": "Rotorua",
                "description": "Hot springs and geothermal wonders — perfect spring getaway.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/d/db/Rotorua_Pohutu_Geyser.jpg",
                "link": "https://www.newzealand.com/nz/rotorua/"
            },
            {
                "name": "Kaikōura",
                "description": "Watch whales and dolphins as the coast blooms with life.",
                "image": "https://upload.wikimedia.org/wikipedia/commons/2/26/Kaikoura_coast.jpg",
                "link": "https://www.newzealand.com/nz/kaikoura/"
            }
        ]


@traveller_bp.route('/ai-trip-planner')
def ai_planner():
    """Page to show all NZ regions from locations.json"""
    traveller_name = session.get('traveller_name', 'Guest Traveller')
    return render_template('traveller/trip_planner_regions.html',
                           traveller_name=traveller_name,
                           locations=NZ_LOCATIONS)
    
    
