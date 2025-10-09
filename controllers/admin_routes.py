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
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
user_model = UserModel()
provider_model = ProviderModel()
ad_model = AdModel()
event_model = EventModel()
blog_model = BlogModel()
journey_model = JourneyModel()
feedback_model = FeedbackModel()
    
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

# 🟤 Display traveller management page
@admin_bp.route("/users")
def manage_users():
    travellers = user_model.db.fetchall("SELECT * FROM users WHERE role='tourist'")
    return render_template("admin/users.html", travellers=travellers)


# 🟤 Add new traveller
@admin_bp.route("/add_traveller", methods=["POST"])
def add_traveller():
    data = request.form
    username = data.get("username")
    email = data.get("email")
    country = data.get("country")

    # Temporary password (you can randomize or send email later)
    password = "123456"

    try:
        user_model.add_user(username, email, password, "tourist", None)
        return jsonify({"status": "success", "message": "Traveller added successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# 🟤 Update traveller
@admin_bp.route("/update_traveller/<int:user_id>", methods=["POST"])
def update_traveller(user_id):
    data = request.form
    username = data.get("username")
    email = data.get("email")
    country = data.get("country")

    try:
        user_model.db.execute(
            "UPDATE users SET username=?, email=?, image=? WHERE id=?",
            (username, email, None, user_id),
        )
        return jsonify({"status": "success", "message": "Traveller updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# 🟤 Delete traveller
@admin_bp.route("/delete_traveller/<int:user_id>", methods=["DELETE"])
def delete_traveller(user_id):
    try:
        user_model.db.execute("DELETE FROM users WHERE id=?", (user_id,))
        return jsonify({"status": "success", "message": "Traveller deleted successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
@admin_bp.route("/users")
def admin_users():
    # Check if logged in as admin
    if "role" not in session or session["role"] != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    # Get current admin
    admin_id = session.get("user_id")
    admin = None
    if admin_id:
        admin = user_model.db.fetchone("SELECT * FROM users WHERE id=?", (admin_id,))

    # Get all travellers (reuse your UserModel method)
    travellers = user_model.get_users_by_role("tourist")

    return render_template(
        "admin/users.html",
        current_admin=admin,
        travellers=travellers
    )
# --- Providers Page ---
@admin_bp.route("/providers")
def admin_providers():
    # Fetch all providers from the new providers table
    providers = provider_model.get_all_providers()
    
    # Fetch all ad requests (pending or approved)
    ads = ad_model.get_all_ads_pending_or_approved()
    
    return render_template("admin/accommodations.html", providers=providers, ads=ads)


# --- Approve Ad ---
@admin_bp.route("/ads/approve/<int:ad_id>", methods=["POST"])
def approve_ad(ad_id):
    ad_model.update_status(ad_id, "Approved")
    return jsonify({"status": "success", "message": "Advertisement approved successfully!"})

# --- Reject Ad ---
@admin_bp.route("/ads/reject/<int:ad_id>", methods=["POST"])
def reject_ad(ad_id):
    ad_model.update_status(ad_id, "Rejected")
    return jsonify({"status": "success", "message": "Advertisement rejected."})

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
    short_description = request.form.get("short_description")
    full_description = request.form.get("full_description")
    image = request.form.get("image")

    blog_model.add_blog(title, short_description, full_description, image)
    return jsonify({"status": "success", "message": "Blog added successfully!"})

# 🟡 Update Blog
@admin_bp.route("/blogs/update/<int:blog_id>", methods=["POST"])
def update_blog(blog_id):
    title = request.form.get("title")
    short_description = request.form.get("short_description")
    full_description = request.form.get("full_description")
    image = request.form.get("image")

    # Reuse add_blog logic (you can create an update method if needed)
    blog_model.db.execute(
        "UPDATE blogs SET title=?, short_description=?, full_description=?, image=? WHERE id=?",
        (title, short_description, full_description, image, blog_id)
    )
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
