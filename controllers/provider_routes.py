from flask import Blueprint, render_template, redirect, url_for, session, flash, request,jsonify
import os
from werkzeug.utils import secure_filename
from models.provider_model import ProviderModel
from models.property_model import PropertyModel
from models.promotion_model import PromotionModel
from models.feedback_model import FeedbackModel
from models.user_model import UserModel
from models.inquiry_model import InquiryModel
from models.database import Database
from controllers.auth_decorators import provider_required

# Initialize Blueprint
provider_bp = Blueprint("provider", __name__, template_folder="../templates/provider")

# Initialize model
provider_model = ProviderModel()
property_model = PropertyModel()
promotion_model = PromotionModel()
feedback_model = FeedbackModel()
user_model = UserModel()
inquiry_model = InquiryModel()
db = Database()

#------------------------------DASHBOARD ----------------------------------------------
@provider_bp.route("/dashboard")
@provider_required
def provider_dashboard():
    """Provider main dashboard"""

    user_id = session.get("user_id")
   
    provider = provider_model.get_current_provider(user_id)
    if not provider:
        flash("Provider profile not found.", "warning")
        return redirect(url_for("login"))
  
    provider_name = provider["username"]
    

    provider_id = provider["id"]

    total_properties = provider_model.count_properties(provider_id)
    total_promotions = promotion_model.count_promotions(provider_id)
    
    inquiries = db.fetchall("""
        SELECT i.*, u.username AS traveller_name, p.name AS property_name,
            m.message AS last_message
        FROM inquiries i
        JOIN users u ON i.traveller_id = u.id
        JOIN properties p ON i.property_id = p.id
        LEFT JOIN inquiry_messages m 
            ON m.inquiry_id = i.id
            AND m.created_at = (SELECT MAX(created_at) FROM inquiry_messages WHERE inquiry_id = i.id)
        WHERE i.provider_id = ?
        ORDER BY i.created_at DESC
    """, (provider_id,))

    total_inquiries = len(inquiries)


    # Get properties overview for chart
    properties = property_model.get_properties_by_provider(provider_id)
    property_types_dict = {}
    for prop in properties:
        ptype = prop["property_type"] or "Other"
        property_types_dict[ptype] = property_types_dict.get(ptype, 0) + 1

    property_types = list(property_types_dict.keys())
    property_counts = list(property_types_dict.values())

    # Promotions stats for chart
    active_promotions = promotion_model.db.fetchone(
        "SELECT COUNT(*) as count FROM promotions WHERE provider_id=? AND status='Confirmed'", (provider_id,)
    )["count"] or 0
    expired_promotions = promotion_model.db.fetchone(
        "SELECT COUNT(*) as count FROM promotions WHERE provider_id=? AND status='Expired'", (provider_id,)
    )["count"] or 0
    
    return render_template(
        "provider/provider_dashboard.html",
        provider=provider,
        provider_name=provider_name,
        total_properties=total_properties,
        total_inquiries=total_inquiries,
        total_promotions=total_promotions,
        property_types=property_types,
        property_counts=property_counts,
        active_promotions=active_promotions,
        expired_promotions=expired_promotions
    )
    
#------------------------------PROPERTY ----------------------------------------------
@provider_bp.route("/properties")
@provider_required
def properties():

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) 
    provider_id = provider["id"]
    properties = property_model.get_properties_by_provider(provider_id)
    return render_template(
        "provider/properties.html",
        properties=properties,
        provider=provider  
    )

# ----------------------------------------------
# ADD PROPERTY
# ----------------------------------------------
@provider_bp.route("/properties/add", methods=["POST"])
@provider_required
def add_property():
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) 
    provider_id = provider["id"]
    if not provider_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    name = request.form.get("name")
    description = request.form.get("description")
    property_type = request.form.get("property_type")
    location = request.form.get("location")
    price_per_day = request.form.get("price_per_day")
    max_guests = request.form.get("max_guests")
    food_available = request.form.get("food_available")
    facilities = request.form.get("facilities")

    # ✅ Handle image upload safely
    image = request.files.get("image")
    filename = None
    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join("static", "images", filename))

    property_model.add_property(
        provider_id, name, description, property_type, location,
        price_per_day, max_guests, food_available, facilities, filename
    )

    flash("Property added successfully!", "success")
    return redirect(url_for("provider.properties"))


# ----------------------------------------------
# UPDATE PROPERTY
# ----------------------------------------------
@provider_bp.route("/properties/update", methods=["POST"])
@provider_required
def update_property():
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) 
    provider_id = provider["id"]
    if not provider_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    property_id = request.form.get("id")
    name = request.form.get("name")
    property_type = request.form.get("property_type")
    location = request.form.get("location")
    price_per_day = request.form.get("price_per_day")
    max_guests = request.form.get("max_guests")
    food_available = request.form.get("food_available")
    facilities = request.form.get("facilities")
    status = request.form.get("status")

    property_model.update_property(
        property_id, name, property_type, location,
        price_per_day, max_guests, food_available,
        facilities, status
    )

    flash("Property updated successfully!", "success")
    return redirect(url_for("provider.properties"))


# ----------------------------------------------
# DELETE PROPERTY
# ----------------------------------------------
@provider_bp.route("/properties/delete/<int:property_id>", methods=["POST"])
@provider_required
def delete_property(property_id):
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) 
    provider_id = provider["id"]
    if not provider_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    property_model.delete_property(property_id)
    flash("Property deleted successfully!", "success")
    return redirect(url_for("provider.properties"))


#------------------------------PROMOTION --------------------------------------------
@provider_bp.route("/promotions", endpoint="promotions")
@provider_required
def provider_promotions():
   
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)
    if not provider:
        flash("Provider profile not found.", "warning")
        return redirect(url_for("provider.profile"))

    promotions = promotion_model.get_promotions_by_provider(provider["id"])

    return render_template(
        "provider/promotions.html",
        provider=provider,
        promotions=promotions,
        new_promotion_approved=True
    )

# -------------------- ADD PROMOTION --------------------
@provider_bp.route('/promotions/add', methods=['GET', 'POST'])
@provider_required
def add_promotion():
    if session.get("role") != "provider":
        return jsonify({"message": "Unauthorized"}), 403

    user_id = session["user_id"]
    provider = provider_model.get_current_provider(user_id)
    if not provider:
        return jsonify({"message": "Provider profile not found"}), 404

    title = request.form.get('title')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    image_file = request.files.get('image')

    image_name = None
    if image_file and image_file.filename:
        image_name = image_file.filename
        image_file.save(f"static/images/{image_name}")

    # Use provider["id"] here!
    promotion_model.add_promotion(provider["id"], title, description, image_name, start_date, end_date)
    return jsonify({'message': 'Promotion request sent for admin approval!'})


# -------------------- UPDATE PROMOTION --------------------
@provider_bp.route('/promotions/update', methods=['POST'])
@provider_required
def update_promotion():
    promo_id = request.form.get('id')
    title = request.form.get('title')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    image_file = request.files.get('image')
    image_name = None
    if image_file and image_file.filename != "":
        image_name = image_file.filename
        image_file.save(f"static/images/promotions/{image_name}")

    promotion_model.update_promotion(promo_id, title, description, image_name, start_date, end_date)
    return jsonify({'message': 'Promotion updated successfully and sent for re-approval!'})


# -------------------- DELETE PROMOTION --------------------
@provider_bp.route('/promotions/delete/<int:promo_id>', methods=['POST'])
def delete_promotion(promo_id):
    promotion_model.delete_promotion(promo_id)
    return jsonify({'message': 'Promotion deleted successfully!'})

#--------------------------------PROFILE ---------------------------------
@provider_bp.route("/profile", methods=["GET"])
@provider_required
def profile():

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) # fetch from session or DB
    return render_template("provider/provider_profile.html", provider=provider)

UPLOAD_FOLDER = "app/static/images"  # Adjust if your folder is different
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@provider_bp.route("/profile/update", methods=["POST"])
@provider_required
def update_profile():
   
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)

    
    hotel_address = request.form.get("hotel_address")
    hotel_name = request.form.get("hotel_name")
    website_url = request.form.get("website_url")


    file = request.files.get("image")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_to_save = filename
    else:
        image_to_save = provider.get("image")  

    
    update_query = """
        UPDATE providers
        SET hotel_name = ?, hotel_address = ?, website_url = ?, image = ?
        WHERE user_id = ?
    """
    provider_model.db.execute(update_query, (hotel_name, hotel_address, website_url, image_to_save, user_id))
    flash("Profile updated successfully!", "success")
    return redirect(url_for("provider.profile"))


#------------------Provider Feedback & Notifications-----------------#
@provider_bp.route("/provider/feedback", methods=["GET"])
@provider_required
def provider_feedback_page():

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)
    feedbacks = feedback_model.get_feedbacks_by_user(user_id, "provider")
    unread_count = feedback_model.get_unread_replies_count(user_id, "provider")

    return render_template(
        "provider/feedback_notifications.html",
        feedbacks=feedbacks,
        provider=provider,
        unread_count=unread_count
    )


@provider_bp.route("/provider/feedback/send", methods=["POST"])
@provider_required
def provider_send_feedback():
 
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)
    user = user_model.get_user_by_id(provider["user_id"])
    provider_name = user["username"]
    provider_email = user["email"]

    message = request.form.get("message")
    if not message:
        return jsonify({"status": "error", "message": "Message cannot be empty"})

    feedback_model.add_feedback(user_id, "provider", provider_name, provider_email, message)
    return jsonify({"status": "success", "message": "Feedback submitted successfully!"})

#------------------Provider Inquiries-----------------#
@provider_bp.route("/provider/inquiries")
@provider_required
def provider_inquiries():
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)
    provider_id = provider["id"]

    inquiries = db.fetchall("""
        SELECT i.*, u.username AS traveller_name, p.name AS property_name,
            m.message AS last_message
        FROM inquiries i
        JOIN users u ON i.traveller_id = u.id
        JOIN properties p ON i.property_id = p.id
        LEFT JOIN inquiry_messages m 
            ON m.inquiry_id = i.id
            AND m.created_at = (SELECT MAX(created_at) FROM inquiry_messages WHERE inquiry_id = i.id)
        WHERE i.provider_id = ?
        ORDER BY i.created_at DESC
    """, (provider_id,))

    return render_template(
        "provider/property_inquiries.html",
        inquiries=inquiries,
        provider=provider
    )



# 💬 Open a chat view for one inquiry
@provider_bp.route("/provider/inquiry/<int:inquiry_id>")
@provider_required
def provider_inquiry_chat(inquiry_id):
   
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)

    # ✅ Use users table instead of travellers
    inquiry = db.fetchone("""
        SELECT i.*, 
               u.username AS traveller_name, 
               p.name AS property_name
        FROM inquiries i
        JOIN users u ON i.traveller_id = u.id
        JOIN properties p ON i.property_id = p.id
        WHERE i.id = ?
    """, (inquiry_id,))

    if not inquiry:
        flash("Inquiry not found.", "danger")
        return redirect(url_for("provider.provider_dashboard"))

    # ✅ Fetch all messages related to this inquiry
    messages = db.fetchall("""
        SELECT m.*, u.username
        FROM inquiry_messages m
        LEFT JOIN users u ON m.sender_id = u.id
        WHERE m.inquiry_id = ?
        ORDER BY m.created_at ASC
    """, (inquiry_id,))

    return render_template("provider/inquiry_chat.html", inquiry=inquiry, messages=messages, provider=provider)


# 📤 Send a reply message
@provider_bp.route("/provider/inquiry/<int:inquiry_id>/send", methods=["POST"])
def provider_send_message(inquiry_id):
    
    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)

    message = request.form.get("message")

    if not message.strip():
        flash("Message cannot be empty.", "warning")
        return redirect(url_for("provider.provider_inquiry_chat", inquiry_id=inquiry_id))

    # ✅ Use provider.user_id (which matches users table)
    db.execute("""
        INSERT INTO inquiry_messages (inquiry_id, sender_id, message)
        VALUES (?, ?, ?)
    """, (inquiry_id, user_id, message))

    db.execute("""
        UPDATE inquiries SET status = 'Open' WHERE id = ?
    """, (inquiry_id,))

    flash("Message sent!", "success")
    return redirect(url_for("provider.provider_inquiry_chat", inquiry_id=inquiry_id))