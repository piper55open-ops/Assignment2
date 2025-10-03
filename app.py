from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from controllers.user_controller import UserController
import os
import json
import math 
import requests
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()  # 🔹 loads .env file into environment

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



app = Flask(__name__)
app.secret_key = "supersecret"  

user_controller = UserController()

@app.route('/')
def home():
    return render_template('home.html')

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        image = None
        if "image" in request.files:
            file = request.files["image"]
            if file.filename:
                image = file.filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], image))

        try:
            user_controller.register_user(username, email, password, role, image)
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        user = user_controller.login_user(email, password)
        if user and user["role"] == role:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            flash("Login successful!", "success")

            if role == "tourist":
                return redirect(url_for("tourist_dashboard"))
            elif role == "provider":
                return redirect(url_for("provider_dashboard"))
            elif role == "admin":
                return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials or role", "danger")

    return render_template("login.html")

client = OpenAI(api_key=OPENAI_API_KEY )
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
    radius = 2000  # 2km search radius
    type_ = "lodging"  # hotels, accommodations

    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius={radius}&type={type_}&key={GOOGLE_API_KEY}"
    )
    response = requests.get(url).json()
    return jsonify(response)


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

@app.route('/stories')
def stories():
    return render_template("stories.html")

@app.route('/discover')
def discover():
    return render_template("discover.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
