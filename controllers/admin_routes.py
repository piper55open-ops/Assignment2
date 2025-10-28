from flask import Blueprint, render_template, session, redirect, url_for, flash,jsonify,request
from flask import Blueprint,current_app
from werkzeug.utils import secure_filename
from models.user_model import UserModel
from models.ad_model import AdModel
from models.provider_model import ProviderModel
from models.event_model import EventModel
from models.blog_model import BlogModel
from models.journey_models import JourneyModel
from models.feedback_model import FeedbackModel
from models.promotion_model import PromotionModel
from models.property_model import PropertyModel
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
user_model = UserModel()
provider_model = ProviderModel()
ad_model = AdModel()
event_model = EventModel()
blog_model = BlogModel()
journey_model = JourneyModel()
feedback_model = FeedbackModel()
promotion_model = PromotionModel()
property_model = PropertyModel()
    
@admin_bp.context_processor
def inject_admin_user():
    admin_id = session.get("user_id")
    admin = None
    if admin_id:
        admin = user_model.db.fetchone(
            "SELECT * FROM users WHERE id=? AND role='admin'",
            (admin_id,)
        )
    return dict(current_admin=admin)

@admin_bp.route("/dashboard")
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))
    total_users = user_model.count_users()
    total_properties = property_model.count_all_properties()  # ✅ You need to create this function
    total_events = event_model.count_events()
    total_blogs = blog_model.count_blogs()

    # Top locations
    top_locations = journey_model.db.fetchall(
        "SELECT location, COUNT(*) AS count FROM journeys "
        "GROUP BY location ORDER BY count DESC LIMIT 5"
    )
    location_labels = [loc["location"] or "Unknown" for loc in top_locations]
    location_data = [loc["count"] for loc in top_locations]

    # Recent journeys & blogs
    recent_journeys = journey_model.get_all_journeys()[:5]
    recent_blogs = blog_model.get_all_blogs()[:5]

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_properties=total_properties,
        total_events=total_events,
        total_blogs= total_blogs,
        regions_labels=location_labels,
        regions_data=location_data,
        recent_journeys=recent_journeys,
        recent_blogs=recent_blogs
    )
@admin_bp.route("/dashboard/users_chart")
def users_chart_data():
    # Fetch counts from your user model
    tourist_count = user_model.count_users_by_role("tourist")
    provider_count = user_model.count_users_by_role("provider")
    admin_count = user_model.count_users_by_role("admin")

    data = {
        "labels": ["Tourist", "Provider", "Admin"],
        "counts": [tourist_count, provider_count, admin_count]
    }
    return jsonify(data)

@admin_bp.route("/dashboard/regions_chart")
def regions_chart_data():
    # Fetch top 5 visited locations
    top_locations = journey_model.db.fetchall(
        "SELECT location, COUNT(*) AS count FROM journeys "
        "GROUP BY location ORDER BY count DESC LIMIT 5"
    )
    labels = [loc["location"] or "Unknown" for loc in top_locations]
    data = [loc["count"] for loc in top_locations]

    return jsonify({
        "labels": labels,
        "counts": data
    })
# Get all users
@admin_bp.route('/users')
def admin_users():
    users = user_model.get_all_users()
    return render_template("admin/users.html", users=users)

# Add new user
@admin_bp.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')
    password = "default123"  # or let admin set

    image_file = request.files.get("image")
    image_name = None
    if image_file and image_file.filename:
        image_name = image_file.filename
        image_file.save(f"static/images/{image_name}")

    try:
        user_model.add_user(username, email, user_model.hash_password(password), role, image_name)
        return jsonify({"status":"success", "message":"User added successfully"})
    except Exception as e:
        return jsonify({"status":"error", "message": str(e)})


# Update user
@admin_bp.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')
    
    image_file = request.files.get("image")
    if image_file and image_file.filename:
        image_name = image_file.filename
        image_file.save(f"static/images/{image_name}")
    else:
        old = user_model.get_user_by_id(user_id)
        image_name = old["image"]  # keep old image if not updated

    user_model.update_profile(user_id, username, email, role, image_name)
    return jsonify({"status":"success", "message":"User updated successfully"})


# Deactivate user
@admin_bp.route('/deactivate_user/<int:user_id>', methods=['POST'])
def deactivate_user(user_id):
    user_model.deactivate_user(user_id)
    return jsonify({"status":"success", "message":"User deactivated successfully"})

# --- Providers Page ---
@admin_bp.route("/providers")
def admin_providers():
    if session.get("role") != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    # Fetch all registered providers
    providers = provider_model.get_all_providers()
    users = user_model.get_users_by_role("provider") 
    # For each provider, fetch their properties
    provider_list = []
    for p in providers:
        properties = property_model.get_properties_by_provider(p["id"])
        provider_list.append({
            "provider": p,
            "properties": properties
        })
    # Fetch promotions by status
    pending_promotions = promotion_model.get_promotions_by_status("Pending")
    confirmed_promotions = promotion_model.get_promotions_by_status("Confirmed")
    rejected_promotions = promotion_model.get_promotions_by_status("Rejected")

    return render_template(
        "admin/accommodations.html",
        providers=providers,
        pending_promotions=pending_promotions,
        confirmed_promotions=confirmed_promotions,
        provider_list=provider_list,
        users=users,
        rejected_promotions=rejected_promotions
    )
    
    # -------------------- ADD PROVIDER --------------------
@admin_bp.route("/providers/add", methods=["POST"])
def add_provider_route():
    user_id = request.form.get("user_id")  # Get selected user from the dropdown
    hotel_name = request.form.get("hotel_name")
    hotel_address = request.form.get("hotel_address")
    website_url = request.form.get("website_url")
    image_file = request.files.get("image")

    image_name = None
    if image_file and image_file.filename:
        image_name = image_file.filename
        image_file.save(f"static/images/{image_name}")

    result = provider_model.add_provider(user_id, hotel_name, hotel_address, website_url, image_name)

    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["message"], "danger")

    return redirect(url_for("admin.admin_providers"))


# -------------------- PROMOTION MANAGEMENT --------------------
@admin_bp.route("/promotions")
def admin_promotions():
    if session.get("role") != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    # Fetch all pending promotions
    pending_promotions = promotion_model.get_promotions_by_status("Pending")
    confirmed_promotions = promotion_model.get_promotions_by_status("Confirmed")
    rejected_promotions = promotion_model.get_promotions_by_status("Rejected")

    return render_template("admin/promotions.html",
                           pending_promotions=pending_promotions,
                           confirmed_promotions=confirmed_promotions,
                           rejected_promotions=rejected_promotions)
    
@admin_bp.route("/promotions/update/<int:promo_id>", methods=["POST"])
def update_promotion_status(promo_id):
    data = request.get_json()
    status = data.get("status")

    if status not in ["Confirmed", "Rejected"]:
        return jsonify({"message": "Invalid status"}), 400

    promotion_model.update_status(promo_id, status)
    return jsonify({"message": f"Promotion {status.lower()} successfully!"})


@admin_bp.route("/promotions/<int:promo_id>/approve", methods=["POST"])
def approve_promotion(promo_id):
    promotion_model.update_status(promo_id, "Confirmed")
    flash("Promotion approved successfully!", "success")
    return redirect(url_for("admin.admin_promotions"))

@admin_bp.route("/promotions/<int:promo_id>/reject", methods=["POST"])
def reject_promotion(promo_id):
    promotion_model.update_status(promo_id, "Rejected")
    flash("Promotion rejected.", "danger")
    return redirect(url_for("admin.admin_promotions"))


#----------------------Events -----------------------------
@admin_bp.route("/events")
def admin_events():
    events = event_model.get_all_events()
    return render_template("admin/events.html", events=events)

@admin_bp.route("/events/add", methods=["POST"])
def add_event():
    title = request.form.get("title")
    description = request.form.get("description")
    date = request.form.get("date")
    location = request.form.get("location")
    image = request.files.get("image")

    if image:
        image.save(f"static/images/events/{image.filename}")
        image_name = image.filename
    else:
        image_name = "default.jpg"

    event_model.add_event(title, description, date, image_name, location)
    return jsonify({"status": "success", "message": "Event added successfully!"})

@admin_bp.route("/events/update/<int:event_id>", methods=["POST"])
def update_event(event_id):
    title = request.form.get("title")
    description = request.form.get("description")
    date = request.form.get("date")
    location = request.form.get("location")
    image = request.files.get("image")

    if image:
        image.save(f"static/images/events/{image.filename}")
        image_name = image.filename
    else:
        old = event_model.get_event_by_id(event_id)
        image_name = old["image"]

    event_model.update_event(event_id, title, description, date, image_name, location)
    return jsonify({"status": "success", "message": "Event updated successfully!"})

@admin_bp.route("/events/delete/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event_model.delete_event(event_id)
    return jsonify({"status": "success", "message": "Event deleted successfully!"})

#-----------------------------BLOGS ---------------------------------------------
# 🟤 Blog Management Dashboard
@admin_bp.route("/blogs")
def admin_blogs():
    blogs = blog_model.get_all_blogs()
    return render_template("admin/blogs.html", blogs=blogs)

# 🟢 Add Blog
@admin_bp.route("/blogs/add", methods=["POST"])
def add_blog():
    title = request.form.get("title")
    author = request.form.get("author") or "Admin"  # Default if not provided
    date = request.form.get("date") or "2025-10-09"  # Optional: auto-fill or use datetime.now().strftime(...)
    short_description = request.form.get("short_description")
    full_description = request.form.get("full_description")
    image = request.form.get("image")

    try:
        blog_model.add_blog(title, author, date, short_description, full_description, image)
        return jsonify({"status": "success", "message": "Blog added successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🟡 Update Blog
@admin_bp.route("/blogs/update/<int:blog_id>", methods=["POST"])
def update_blog(blog_id):
    title = request.form.get("title")
    author = request.form.get("author") or "Admin"
    date = request.form.get("date") or "2025-10-09"
    short_description = request.form.get("short_description")
    full_description = request.form.get("full_description")
    image = request.form.get("image")

    blog_model.update_blog(blog_id, title, author, date, short_description, full_description, image)
    return jsonify({"status": "success", "message": "Blog updated successfully!"})

# 🔴 Delete Blog
@admin_bp.route("/blogs/delete/<int:blog_id>", methods=["DELETE"])
def delete_blog(blog_id):
    blog_model.delete_blog(blog_id)
    return jsonify({"status": "success", "message": "Blog deleted successfully!"})


#--------------------------------------Analytics--------------------------------
@admin_bp.route("/analytics")
def admin_analytics():
    # Get statistics
    total_travellers = user_model.count_users_by_role("tourist")
    total_providers = user_model.count_users_by_role("provider")
    total_locations = journey_model.count_journeys()
    active_events = event_model.count_events()
    total_blogs = blog_model.count_blogs()

    # Data for charts
    users_by_role = {
        "Tourist": total_travellers,
        "Provider": total_providers
    }

    top_regions = [
        {"region": "Queenstown", "visits": 120},
        {"region": "Auckland", "visits": 95},
        {"region": "Rotorua", "visits": 85},
        {"region": "Wellington", "visits": 80},
        {"region": "Christchurch", "visits": 75},
    ]

    monthly_signups = [
        {"month": "Jan", "signups": 20},
        {"month": "Feb", "signups": 30},
        {"month": "Mar", "signups": 25},
        {"month": "Apr", "signups": 40},
        {"month": "May", "signups": 35},
        {"month": "Jun", "signups": 50},
    ]

    return render_template(
        "admin/analytics.html",
        users_by_role=users_by_role,
        total_locations=total_locations,
        active_events=active_events,
        total_blogs=total_blogs,
        top_regions=top_regions,
        monthly_signups=monthly_signups
    )
#----------------------------- Settings --------------------------------

    
@admin_bp.route("/settings")
def admin_settings():
    if "role" not in session or session["role"] != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    return render_template("admin/settings.html")

@admin_bp.route("/settings/logo", methods=["POST"])
def update_logo():
    file = request.files.get("logo")
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    return jsonify({"status": "success", "message": "Logo updated!"})

@admin_bp.route("/settings/colors", methods=["POST"])
def update_colors():
    # Save colors to config table or a JSON file
    primary = request.form.get("primary_color")
    secondary = request.form.get("secondary_color")
    return jsonify({"status": "success", "message": "Colors updated!"})

@admin_bp.route("/settings/footer", methods=["POST"])
def update_footer():
    footer_text = request.form.get("footer_text")
    email = request.form.get("footer_email")
    phone = request.form.get("footer_phone")
    # Save to config table
    return jsonify({"status": "success", "message": "Footer updated!"})

@admin_bp.route("/settings/admins", methods=["POST"])
def add_admin():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    file = request.files.get("image")
    image = file.filename if file else None
    # Save admin user to users table
    user_model.add_user(username, email, password, "admin", image)
    return jsonify({"status": "success", "message": "New admin added!"})

#--------------------------Feedback Page ----------------------------
# 📝 Admin Feedback Page
@admin_bp.route("/feedbacks")
def admin_feedbacks():
    feedbacks = feedback_model.get_all_feedbacks()
    return render_template("admin/feedback.html", feedbacks=feedbacks)

# 💬 Reply / Update Feedback
@admin_bp.route("/feedback/reply/<int:feedback_id>", methods=["POST"])
def reply_feedback(feedback_id):
    reply = request.form.get("reply")
    status = request.form.get("status")
    try:
        feedback_model.update_feedback(feedback_id, reply, status)
        return jsonify({"status": "success", "message": "Feedback updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ❌ Delete Feedback
@admin_bp.route("/feedback/delete/<int:feedback_id>", methods=["DELETE"])
def delete_feedback(feedback_id):
    try:
        feedback_model.delete_feedback(feedback_id)
        return jsonify({"status": "success", "message": "Feedback deleted successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
