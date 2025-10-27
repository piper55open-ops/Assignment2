from flask import Blueprint, render_template, redirect, url_for, session, flash, request,jsonify
import os
from werkzeug.utils import secure_filename
from models.provider_model import ProviderModel
from models.property_model import PropertyModel
from models.promotion_model import PromotionModel


# Initialize Blueprint
provider_bp = Blueprint("provider", __name__, template_folder="../templates/provider")

# Initialize model
provider_model = ProviderModel()
property_model = PropertyModel()
promotion_model = PromotionModel()

@provider_bp.route("/dashboard")
def provider_dashboard():
    """Provider main dashboard"""
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)
    if not provider:
        flash("Provider profile not found.", "warning")
        return redirect(url_for("login"))

    provider_id = provider["id"]
    total_properties = provider_model.count_properties(user_id)
    total_promotions = promotion_model.count_promotions(user_id)
    profile_completion = provider_model.calculate_profile_completion(provider)

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
        total_properties=total_properties,
        total_promotions=total_promotions,
        profile_completion=profile_completion,
        property_types=property_types,
        property_counts=property_counts,
        active_promotions=active_promotions,
        expired_promotions=expired_promotions
    )
#------------------------------PROPERTY ----------------------------------------------
@provider_bp.route("/properties")
def properties():
    if session.get("role") != "provider":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) 
    properties = property_model.get_properties_by_provider(user_id)
    return render_template(
        "provider/properties.html",
        properties=properties,
        provider=provider  
    )

@provider_bp.route("/properties/add", methods=["POST"])
def add_property():
    if "provider_id" not in session:
        return jsonify({"message": "Unauthorized"}), 403

    provider_id = session["provider_id"]
    name = request.form.get("name")
    description = request.form.get("description")
    property_type = request.form.get("property_type")
    location = request.form.get("location")
    price_per_day = request.form.get("price_per_day")
    max_guests = request.form.get("max_guests")
    food_available = request.form.get("food_available")
    facilities = request.form.get("facilities")

    # Handle image upload
    image = request.files.get("image")
    filename = None
    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join("static", "images", filename))

    property_model.add_property(
        provider_id, name, description, property_type, location,
        price_per_day, max_guests, food_available, facilities, filename
    )

    return jsonify({"message": "Property added successfully!"})

@provider_bp.route("/properties/update", methods=["POST"])
def update_property():
    if "provider_id" not in session:
        return jsonify({"message": "Unauthorized"}), 403

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

    return jsonify({"message": "Property updated successfully!"})

@provider_bp.route("/properties/delete/<int:property_id>", methods=["POST"])
def delete_property(property_id):
    if "provider_id" not in session:
        return jsonify({"message": "Unauthorized"}), 403

    property_model.delete_property(property_id)
    return jsonify({"message": "Property deleted successfully!"})


#------------------------------PROMOTION --------------------------------------------
# -------------------- VIEW PROMOTIONS --------------------
@provider_bp.route("/promotions", endpoint="promotions")
def provider_promotions():
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

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
def profile():
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id) # fetch from session or DB
    return render_template("provider/provider_profile.html", provider=provider)

UPLOAD_FOLDER = "app/static/images"  # Adjust if your folder is different
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@provider_bp.route("/profile/update", methods=["POST"])
def update_profile():
    if "role" not in session or session["role"] != "provider":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    provider = provider_model.get_current_provider(user_id)

    # Get form data
    hotel_address = request.form.get("hotel_address")
    hotel_name = request.form.get("hotel_name")
    website_url = request.form.get("website_url")

    # Handle image upload
    file = request.files.get("image")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_to_save = filename
    else:
        image_to_save = provider.get("image")  # Keep existing image if no new upload

    # Update provider in DB
    update_query = """
        UPDATE providers
        SET hotel_name = ?, hotel_address = ?, website_url = ?, image = ?
        WHERE user_id = ?
    """
    provider_model.db.execute(update_query, (hotel_name, hotel_address, website_url, image_to_save, user_id))
    flash("Profile updated successfully!", "success")
    return redirect(url_for("provider.profile"))