from flask import Blueprint, render_template, request, jsonify
import json, os

trip_planner_bp = Blueprint("trip_planner", __name__, url_prefix="/trip-planner")

# ✅ Load all NZ regions and coordinates from JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_FILE = os.path.join(BASE_DIR, "..", "data", "locations.json")

def load_locations():
    with open(LOCATIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

@trip_planner_bp.route("/")
def select_region():
    """Display all regions dynamically from JSON."""
    regions = load_locations()
    return render_template("trip_planner_regions.html", regions=regions)


@trip_planner_bp.route('/trip-planner')
def trip_planner_regions():
    """Show all New Zealand regions (states)"""
    locations = load_locations()
    return render_template('traveller/trip_planner_regions.html', locations=locations)

@trip_planner_bp.route('/trip-planner/places/<region_name>')
def trip_planner_places(region_name):
    """Show places and trip planner for the selected region"""
    locations = load_locations()

    if region_name not in locations:
        return render_template('404.html', message="Region not found"), 404

    region = locations[region_name]

    # You can later replace this static list with dynamic data or API
    places = [
        {"name": "City Center", "image": "auckland_city.jpg", "desc": "Explore the vibrant heart of Auckland."},
        {"name": "Beaches", "image": "piha_beach.jpg", "desc": "Relax at Piha or Mission Bay."},
        {"name": "Mountains", "image": "rangitoto.jpg", "desc": "Climb Rangitoto Island for panoramic views."}
    ]

    return render_template(
        'traveller/trip_planner_places.html',
        region_name=region_name,
        region=region,
        places=places
    )