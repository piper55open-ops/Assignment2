from flask import Blueprint, render_template, request, redirect, send_file, url_for,flash, jsonify,session
import os
import json
from werkzeug.utils import secure_filename
import math
from io import BytesIO
import time
import requests
from dotenv import load_dotenv
from flask import Flask, session
from openai import OpenAI

from controllers.user_controller import UserController
from models.user_model import UserModel
from models.journey_models import JourneyModel
from models.blog_model import BlogModel
from models.provider_model import ProviderModel
from models.property_model import PropertyModel
from models.promotion_model import PromotionModel
from models.event_model import EventModel
from controllers.admin_routes import admin_bp
from controllers.provider_routes import provider_bp
from controllers.traveller_routes import traveller_bp

load_dotenv()  # 🔹 loads .env file into environment

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)
app.secret_key = "super_secret_key_123" 

user_controller = UserController()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID"),
    project=os.getenv("OPENAI_PROJECT_ID")
)
user_model = UserModel()
journey_model = JourneyModel()
blog_model = BlogModel()
provider_model = ProviderModel()
property_model = PropertyModel()
promotion_model = PromotionModel()
event_model = EventModel()

print("OpenAI Key Loaded:", os.getenv("OPENAI_API_KEY"))

@app.route('/')
def home():
    return render_template('home.html')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file.filename:
                # secure the filename
                filename = secure_filename(file.filename)
                new_filename = f"{role}_{int(time.time())}_{filename}"
                # save inside static/images
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))
                image_filename = new_filename

        try:
            # save user with image_filename
            user_controller.register_user(username, email, password, role, image_filename)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template("auth/register.html")


# -------------------- LOGIN --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].lower().strip()

        user = user_controller.login_user(email, password)

        if user and user["role"].lower() == role:
            session["user_id"] = user["id"]
            session["role"] = user["role"].lower()
            flash("Login successful!", "success")
            print("SESSION DATA:", dict(session)) 

            if role == "tourist":
                return redirect(url_for("traveller.traveller_dashboard"))
            elif role == "provider":
                return redirect(url_for("provider.provider_dashboard"))
            elif role == "admin":
                return redirect(url_for("admin.admin_dashboard"))
        else:
            flash("Invalid credentials or role", "danger")

    return render_template("auth/login.html")


# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/locations")
def locations():
    file_path = os.path.join(app.root_path, "data", "blogs.json")
    with open(file_path, "r", encoding="utf-8") as f:
        blogs = json.load(f)
        page = request.args.get('page', 1, type=int)
        per_page = 6 # number of blogs per page
        start = (page - 1) * per_page
        end = start + per_page
        total_pages = math.ceil(len(blogs) / per_page)
        paginated_blogs = blogs[start:end]
    return render_template(
            "locations.html",
            blogs=paginated_blogs,  
            all_blogs=blogs,        
            total_pages=total_pages,
            prev_page=page-1 if page>1 else None,
            next_page=page+1 if page<total_pages else None,
            sidebar_posts=blogs[:4],  # top posts
            tags=["Architecture","Exterior","Interior","Planning","Gardening","Landscape"]
)

@app.route("/blog/<int:blog_id>")
def blog_detail(blog_id):
    file_path = os.path.join(app.root_path, "data", "blogs.json")
    with open(file_path, "r", encoding="utf-8") as f:
        blogs = json.load(f)

    blog = next((b for b in blogs if b["id"] == blog_id), None)
    if blog is None:
        return "Blog not found", 404

    return render_template(
        "blog_detail.html",
        blog=blog,
        google_api_key=GOOGLE_API_KEY
    )


# 🔹 Proxy for Google Places API
@app.route("/places_proxy")
def places_proxy():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    radius = request.args.get("radius", 2000)
    type_ = request.args.get("type", "lodging")  # default to lodging if not provided

    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius={radius}&type={type_}&key={GOOGLE_API_KEY}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)



# 🔹 AI Smart Recommendations

@app.route("/ai_recommend", methods=["POST"])
def ai_recommend():
    data = request.get_json()
    location = data.get("location", "")
    traveler_type = data.get("traveler_type", "budget traveler")

    prompt = f"Suggest the best accommodations near {location} for {traveler_type}. Include names, budget range, and reasons."

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # use your available model
        messages=[
            {"role": "system", "content": "You are a travel assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return jsonify({"recommendations": response.choices[0].message.content})

@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    data = request.get_json()
    user_question = data.get("question", "")

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Or "gpt-4o", "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a travel assistant."},
            {"role": "user", "content": user_question}
        ]
    )

    return jsonify({"answer": response.choices[0].message.content})

@app.route('/journies')
def journies():
    events = event_model.get_all_events()  # List of all events
    # Split into chunks of 3 for each row
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    event_rows = list(chunks(events, 3))
    return render_template('journeys.html', event_rows=event_rows)



@app.route('/discover')
def discover():
    # Get the absolute path to locations.json
    base_dir = os.path.abspath(os.path.dirname(__file__))  # directory of app.py
    json_path = os.path.join(base_dir, "data", "locations.json")

    with open(json_path, "r", encoding="utf-8") as f:
        regions = json.load(f)

    return render_template("discover.html", regions=regions)

@app.route("/discover_places_proxy")
def discover_places_proxy():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    if not lat or not lng:
        return jsonify({"error": "Missing lat or lng"}), 400

    # Google Places Nearby Search
    places_url = (
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius=2000&type=restaurant&key={GOOGLE_API_KEY}"
    )

    places_res = requests.get(places_url)
    if places_res.status_code != 200:
        return jsonify({"error": "Failed to fetch places"}), 500

    data = places_res.json()
    results = []

    for place in data.get("results", []):
        photo_url = ""
        if "photos" in place and len(place["photos"]) > 0:
            # Instead of returning Google's URL, return our own endpoint
            photo_ref = place["photos"][0]["photo_reference"]
            photo_url = f"/places_photo?photoref={photo_ref}"

        results.append({
            "name": place.get("name"),
            "photo_url": photo_url,
            "vicinity": place.get("formatted_address", ""),
            "geometry": place.get("geometry", {})
        })

    return jsonify({"results": results})

@app.route("/places_photo")
def places_photo():
    photoref = request.args.get("photoref")
    if not photoref:
        return "No photo reference provided", 400

    # Google Place Photo URL
    google_photo_url = (
        f"https://maps.googleapis.com/maps/api/place/photo"
        f"?maxwidth=400&photoreference={photoref}&key={GOOGLE_API_KEY}"
    )

    # Fetch the image from Google
    response = requests.get(google_photo_url)
    if response.status_code != 200:
        return "Failed to fetch photo", response.status_code

    # Convert content to a BytesIO stream
    img_stream = BytesIO(response.content)

    # Serve image as file
    return send_file(img_stream, mimetype="image/jpeg")

# ================== Chatbot API Route ==================

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_message = request.json.get("message", "")
    if not user_message.strip():
        return jsonify({"response": "Please type a message."})

    try:
        # Simple AI or placeholder logic
        if "hello" in user_message.lower():
            bot_reply = "Hello traveller! 😊 How can I help you plan your next trip?"
        elif "recommend" in user_message.lower():
            bot_reply = "I recommend visiting Queenstown for adventure or Rotorua for culture!"
        elif "thank" in user_message.lower():
            bot_reply = "You're most welcome! 🧳"
        else:
            bot_reply = "I'm here to help you with travel tips and planning ideas!"

        return jsonify({"response": bot_reply})

    except Exception as e:
        print("Chatbot Error:", e)
        return jsonify({"response": "Sorry, I’m having trouble responding right now. Please try again soon."})
    
@app.route("/chatbot_reply", methods=["POST"])
def chatbot_reply():
    data = request.get_json()
    user_message = data.get("message", "")

    # Very basic AI logic for now
    if "hello" in user_message.lower():
        reply = "Hi there! How can I help you explore New Zealand today?"
    elif "place" in user_message.lower() or "visit" in user_message.lower():
        reply = "There are so many beautiful places! Try visiting Hobbiton, Queenstown, or Rotorua!"
    else:
        reply = "I'm still learning. Try asking me about places or travel tips in New Zealand."

    return jsonify({"reply": reply})


# -------------------- DASHBOARDS ---------------------------------------
#--------------------------ADMIN DASHBOARD ------------------------------


app.register_blueprint(admin_bp)


#--------------------------ADMIN DASHBOARD END ------------------------------

#--------------------------PROVIDER DASHBOARD------------------------------

app.register_blueprint(provider_bp)

#--------------------------PROVIDER DASHBOARD END------------------------------
#--------------------------TRAVELLER DASHBOARD -------------------------------
app.register_blueprint(traveller_bp)
#--------------------------TRAVELLER DASHBOARD -------------------------------


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=80)
    
